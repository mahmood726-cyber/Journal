"""
AI-powered reviewer matching service using local LLM embeddings.
Finds the best reviewers for manuscripts using semantic similarity.
"""
from typing import List, Dict, Optional, Tuple
from pydantic import BaseModel
from datetime import datetime
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from .llm_service import get_llm_service, LocalLLMService
from ..db.models import User, Manuscript, Review, UserRole, ReviewStatus
from ..core.config import settings


class ReviewerMatch(BaseModel):
    """A reviewer match with similarity score and reasoning."""
    reviewer_id: int
    reviewer_name: str
    email: str
    affiliation: Optional[str]
    orcid: Optional[str]
    specializations: List[str]
    similarity_score: float
    match_reasons: List[str]
    past_reviews_count: int
    average_review_time_days: Optional[float]
    current_workload: int  # Number of pending/in-progress reviews
    availability_status: str  # "available", "busy", "overloaded"


class ReviewerMatchingReport(BaseModel):
    """Complete reviewer matching report."""
    manuscript_id: int
    manuscript_title: str
    matches: List[ReviewerMatch]
    total_candidates: int
    matching_method: str
    matched_at: datetime


class AIReviewerMatchingService:
    """
    AI-powered reviewer matching using local LLM embeddings.

    Features:
    - Semantic similarity between manuscript and reviewer expertise
    - Consideration of reviewer workload
    - Past performance metrics
    - AI-generated match explanations
    """

    def __init__(
        self,
        llm_service: Optional[LocalLLMService] = None,
        similarity_threshold: float = None,
        top_k: int = None
    ):
        """Initialize reviewer matching service."""
        self.llm = llm_service or get_llm_service()
        self.similarity_threshold = similarity_threshold or settings.REVIEWER_MATCH_THRESHOLD
        self.top_k = top_k or settings.REVIEWER_TOP_K

    async def find_best_reviewers(
        self,
        manuscript_id: int,
        num_reviewers: int = 5,
        exclude_author_ids: Optional[List[int]] = None,
        db: Session = None
    ) -> ReviewerMatchingReport:
        """
        Find best reviewer matches for a manuscript.

        Args:
            manuscript_id: ID of manuscript to find reviewers for
            num_reviewers: Number of top matches to return
            exclude_author_ids: List of author IDs to exclude (conflict of interest)
            db: Database session

        Returns:
            ReviewerMatchingReport with top matches
        """
        # Get manuscript
        manuscript = db.query(Manuscript).filter(Manuscript.id == manuscript_id).first()
        if not manuscript:
            raise ValueError(f"Manuscript {manuscript_id} not found")

        # Build manuscript text for matching
        manuscript_text = self._build_manuscript_text(manuscript)

        # Generate manuscript embedding
        manuscript_embedding = await self._get_embedding(manuscript_text)

        # Get all potential reviewers
        potential_reviewers = self._get_potential_reviewers(
            db,
            exclude_author_ids=exclude_author_ids or []
        )

        # Calculate matches
        matches = []
        for reviewer in potential_reviewers:
            # Build reviewer profile
            reviewer_profile = self._build_reviewer_profile(reviewer, db)

            # Generate reviewer embedding
            reviewer_embedding = await self._get_embedding(reviewer_profile['text'])

            # Calculate similarity
            similarity = float(cosine_similarity(
                manuscript_embedding.reshape(1, -1),
                reviewer_embedding.reshape(1, -1)
            )[0][0])

            # Only include if above threshold
            if similarity >= self.similarity_threshold:
                # Get reviewer metrics
                metrics = self._get_reviewer_metrics(reviewer.id, db)

                # Determine availability
                availability = self._determine_availability(metrics['current_workload'])

                matches.append({
                    'reviewer': reviewer,
                    'similarity_score': similarity,
                    'profile': reviewer_profile,
                    'metrics': metrics,
                    'availability': availability
                })

        # Sort by similarity (highest first)
        matches.sort(key=lambda x: x['similarity_score'], reverse=True)

        # Take top N matches
        top_matches = matches[:num_reviewers]

        # Generate AI explanations for matches
        analyzed_matches = await self._generate_match_explanations(
            manuscript,
            top_matches
        )

        return ReviewerMatchingReport(
            manuscript_id=manuscript.id,
            manuscript_title=manuscript.title,
            matches=analyzed_matches,
            total_candidates=len(potential_reviewers),
            matching_method="semantic_similarity_local_llm",
            matched_at=datetime.utcnow()
        )

    def _build_manuscript_text(self, manuscript: Manuscript) -> str:
        """Build text representation of manuscript for matching."""
        parts = [
            f"Title: {manuscript.title}",
            f"Abstract: {manuscript.abstract}",
        ]

        if manuscript.keywords:
            parts.append(f"Keywords: {', '.join(manuscript.keywords)}")

        if manuscript.specialization:
            parts.append(f"Field: {manuscript.specialization.name}")

        return "\n\n".join(parts)

    def _build_reviewer_profile(self, reviewer: User, db: Session) -> Dict:
        """Build text representation of reviewer for matching."""
        parts = [f"Reviewer: {reviewer.full_name}"]

        if reviewer.specializations:
            spec_names = [s.name for s in reviewer.specializations]
            parts.append(f"Expertise: {', '.join(spec_names)}")

        if reviewer.bio:
            parts.append(f"Bio: {reviewer.bio[:500]}")

        if reviewer.affiliation:
            parts.append(f"Affiliation: {reviewer.affiliation}")

        # Get past reviews to understand reviewing experience
        past_reviews = db.query(Review).filter(
            Review.reviewer_id == reviewer.id,
            Review.status == ReviewStatus.COMPLETED
        ).limit(10).all()

        if past_reviews:
            review_titles = []
            for review in past_reviews:
                if review.manuscript and review.manuscript.title:
                    review_titles.append(review.manuscript.title)

            if review_titles:
                parts.append(f"Recent reviews: {'; '.join(review_titles[:5])}")

        profile_text = "\n".join(parts)

        return {
            'text': profile_text,
            'specializations': [s.name for s in reviewer.specializations],
            'past_reviews': len(past_reviews)
        }

    def _get_potential_reviewers(
        self,
        db: Session,
        exclude_author_ids: List[int]
    ) -> List[User]:
        """Get all potential reviewers from database."""
        query = db.query(User).filter(
            User.role.in_([UserRole.REVIEWER, UserRole.EDITOR, UserRole.ASSOCIATE_EDITOR]),
            User.is_active == True,
            User.is_verified == True
        )

        if exclude_author_ids:
            query = query.filter(~User.id.in_(exclude_author_ids))

        return query.all()

    def _get_reviewer_metrics(self, reviewer_id: int, db: Session) -> Dict:
        """Get reviewer performance metrics."""
        # Count past reviews
        completed_reviews = db.query(Review).filter(
            Review.reviewer_id == reviewer_id,
            Review.status == ReviewStatus.COMPLETED
        ).all()

        # Calculate average review time
        review_times = []
        for review in completed_reviews:
            if review.accepted_at and review.completed_at:
                time_diff = (review.completed_at - review.accepted_at).days
                review_times.append(time_diff)

        avg_time = sum(review_times) / len(review_times) if review_times else None

        # Count current workload
        current_workload = db.query(Review).filter(
            Review.reviewer_id == reviewer_id,
            Review.status.in_([ReviewStatus.PENDING, ReviewStatus.IN_PROGRESS])
        ).count()

        return {
            'past_reviews_count': len(completed_reviews),
            'average_review_time_days': avg_time,
            'current_workload': current_workload
        }

    def _determine_availability(self, current_workload: int) -> str:
        """Determine reviewer availability based on workload."""
        if current_workload == 0:
            return "available"
        elif current_workload <= 2:
            return "busy"
        else:
            return "overloaded"

    async def _generate_match_explanations(
        self,
        manuscript: Manuscript,
        matches: List[Dict]
    ) -> List[ReviewerMatch]:
        """Generate AI explanations for why each reviewer matches."""
        analyzed_matches = []

        for match in matches:
            reviewer = match['reviewer']
            profile = match['profile']
            metrics = match['metrics']

            # Generate explanation using LLM
            reasons = await self._explain_match(
                manuscript=manuscript,
                reviewer=reviewer,
                profile_text=profile['text'],
                similarity_score=match['similarity_score']
            )

            analyzed_matches.append(ReviewerMatch(
                reviewer_id=reviewer.id,
                reviewer_name=reviewer.full_name,
                email=reviewer.email,
                affiliation=reviewer.affiliation,
                orcid=reviewer.orcid,
                specializations=profile['specializations'],
                similarity_score=match['similarity_score'],
                match_reasons=reasons,
                past_reviews_count=metrics['past_reviews_count'],
                average_review_time_days=metrics['average_review_time_days'],
                current_workload=metrics['current_workload'],
                availability_status=match['availability']
            ))

        return analyzed_matches

    async def _explain_match(
        self,
        manuscript: Manuscript,
        reviewer: User,
        profile_text: str,
        similarity_score: float
    ) -> List[str]:
        """Use LLM to explain why reviewer is a good match."""
        prompt = f"""Explain why this reviewer is a good match for this manuscript.

Manuscript:
- Title: {manuscript.title}
- Abstract: {manuscript.abstract[:300]}
- Keywords: {', '.join(manuscript.keywords) if manuscript.keywords else 'None'}

Reviewer Profile:
{profile_text[:500]}

Similarity Score: {similarity_score:.2%}

Provide exactly 3 specific reasons why they match.
Each reason should be one concise sentence.
Focus on expertise overlap and qualifications.

Format:
1. [First reason]
2. [Second reason]
3. [Third reason]
"""

        try:
            response = await self.llm.generate(
                prompt=prompt,
                temperature=0.5,
                max_tokens=150,
                cache_key=self._get_cache_key(manuscript.id, reviewer.id)
            )

            # Parse reasons from response
            reasons = self._parse_reasons(response.text)

            # Ensure we have exactly 3 reasons
            if len(reasons) < 3:
                reasons.extend([
                    f"High expertise match ({similarity_score:.1%} similarity)",
                    "Qualified reviewer in relevant field",
                    "Active reviewer with appropriate experience"
                ][:3 - len(reasons)])

            return reasons[:3]

        except Exception as e:
            # Fallback reasons if LLM fails
            return [
                f"Strong semantic match ({similarity_score:.1%} similarity) between manuscript and reviewer expertise",
                "Reviewer specialization aligns with manuscript topic area",
                "Qualified reviewer with relevant background"
            ]

    def _parse_reasons(self, text: str) -> List[str]:
        """Parse numbered reasons from LLM response."""
        import re

        # Look for numbered list patterns
        patterns = [
            r'^\d+\.\s*(.+)$',  # 1. Reason
            r'^-\s*(.+)$',      # - Reason
            r'^\*\s*(.+)$',     # * Reason
        ]

        reasons = []
        lines = text.strip().split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            for pattern in patterns:
                match = re.match(pattern, line)
                if match:
                    reason = match.group(1).strip()
                    if reason and len(reason) > 10:  # Valid reason
                        reasons.append(reason)
                    break

        return reasons

    async def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding from local LLM."""
        response = await self.llm.embed(
            text=text,
            cache_key=self._get_cache_key(text[:100])
        )
        return np.array(response.embedding)

    def _get_cache_key(self, *args) -> str:
        """Generate cache key."""
        import hashlib
        key_str = "|".join(str(arg) for arg in args)
        return hashlib.md5(key_str.encode()).hexdigest()


# Singleton instance
_reviewer_matching_service: Optional[AIReviewerMatchingService] = None


def get_reviewer_matching_service() -> AIReviewerMatchingService:
    """Get singleton reviewer matching service instance."""
    global _reviewer_matching_service
    if _reviewer_matching_service is None:
        _reviewer_matching_service = AIReviewerMatchingService()
    return _reviewer_matching_service
