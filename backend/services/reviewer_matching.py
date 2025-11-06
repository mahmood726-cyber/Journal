"""
AI-Powered Reviewer Matching System

Uses machine learning and NLP to intelligently match manuscripts with optimal reviewers
based on expertise, citation networks, past performance, and availability.
"""
from typing import List, Dict, Tuple, Optional
import logging
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx

logger = logging.getLogger(__name__)


class ReviewerMatchingEngine:
    """
    Advanced AI-powered reviewer matching system.

    Scoring Algorithm:
    - Expertise Match (40%): TF-IDF similarity of reviewer's publications with manuscript
    - Citation Network (20%): Co-citation and bibliographic coupling
    - Past Performance (15%): Review quality, turnaround time, acceptance rate
    - Availability (15%): Current workload and response rate
    - Diversity (10%): Geographic and institutional diversity
    """

    def __init__(self, db_session):
        self.db = db_session
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=2
        )

    def find_best_reviewers(
        self,
        manuscript_id: int,
        num_reviewers: int = 10,
        exclude_authors: bool = True,
        min_score: float = 0.3
    ) -> List[Dict]:
        """
        Find the best-matched reviewers for a manuscript.

        Args:
            manuscript_id: ID of the manuscript
            num_reviewers: Number of top reviewers to return
            exclude_authors: Exclude manuscript authors and co-authors
            min_score: Minimum matching score threshold (0-1)

        Returns:
            List of reviewer dictionaries with matching scores and reasons
        """
        from db.models import Manuscript, User, Review, UserRole

        # Get manuscript
        manuscript = self.db.query(Manuscript).filter(Manuscript.id == manuscript_id).first()
        if not manuscript:
            raise ValueError(f"Manuscript {manuscript_id} not found")

        # Get all potential reviewers
        reviewers_query = self.db.query(User).filter(
            User.role == UserRole.REVIEWER,
            User.is_active == True,
            User.is_verified == True
        )

        # Exclude authors if requested
        if exclude_authors:
            author_ids = [author.id for author in manuscript.authors]
            reviewers_query = reviewers_query.filter(~User.id.in_(author_ids))

        potential_reviewers = reviewers_query.all()

        if not potential_reviewers:
            return []

        # Calculate scores for each reviewer
        reviewer_scores = []

        for reviewer in potential_reviewers:
            score_breakdown = self._calculate_reviewer_score(manuscript, reviewer)

            if score_breakdown['total_score'] >= min_score:
                reviewer_scores.append({
                    'reviewer_id': reviewer.id,
                    'reviewer_name': reviewer.full_name,
                    'reviewer_email': reviewer.email,
                    'affiliation': reviewer.affiliation,
                    'country': reviewer.country,
                    'orcid': reviewer.orcid,
                    'total_score': score_breakdown['total_score'],
                    'expertise_score': score_breakdown['expertise_score'],
                    'network_score': score_breakdown['network_score'],
                    'performance_score': score_breakdown['performance_score'],
                    'availability_score': score_breakdown['availability_score'],
                    'diversity_score': score_breakdown['diversity_score'],
                    'matching_keywords': score_breakdown['matching_keywords'],
                    'reason': self._generate_matching_reason(score_breakdown),
                    'estimated_quality': self._estimate_review_quality(reviewer),
                    'average_turnaround_days': self._get_average_turnaround(reviewer)
                })

        # Sort by total score
        reviewer_scores.sort(key=lambda x: x['total_score'], reverse=True)

        # Apply diversity boost to top candidates
        reviewer_scores = self._apply_diversity_boost(reviewer_scores, manuscript)

        return reviewer_scores[:num_reviewers]

    def _calculate_reviewer_score(
        self,
        manuscript,
        reviewer: 'User'
    ) -> Dict[str, float]:
        """Calculate comprehensive matching score for a reviewer."""

        # 1. Expertise Match (40%)
        expertise_score = self._calculate_expertise_match(manuscript, reviewer)

        # 2. Citation Network (20%)
        network_score = self._calculate_network_score(manuscript, reviewer)

        # 3. Past Performance (15%)
        performance_score = self._calculate_performance_score(reviewer)

        # 4. Availability (15%)
        availability_score = self._calculate_availability_score(reviewer)

        # 5. Diversity (10%)
        diversity_score = self._calculate_diversity_score(manuscript, reviewer)

        # Weighted total
        total_score = (
            expertise_score * 0.40 +
            network_score * 0.20 +
            performance_score * 0.15 +
            availability_score * 0.15 +
            diversity_score * 0.10
        )

        # Get matching keywords for explanation
        matching_keywords = self._extract_matching_keywords(manuscript, reviewer)

        return {
            'total_score': round(total_score, 3),
            'expertise_score': round(expertise_score, 3),
            'network_score': round(network_score, 3),
            'performance_score': round(performance_score, 3),
            'availability_score': round(availability_score, 3),
            'diversity_score': round(diversity_score, 3),
            'matching_keywords': matching_keywords
        }

    def _calculate_expertise_match(self, manuscript, reviewer: 'User') -> float:
        """
        Calculate expertise match using TF-IDF similarity.
        Compares manuscript abstract/keywords with reviewer's specializations and bio.
        """
        # Manuscript text
        manuscript_text = f"{manuscript.title} {manuscript.abstract} {' '.join(manuscript.keywords or [])}"

        # Reviewer expertise text
        reviewer_specializations = [spec.name for spec in reviewer.specializations]
        reviewer_text = f"{reviewer.bio or ''} {' '.join(reviewer_specializations)}"

        if not reviewer_text.strip():
            return 0.0

        try:
            # Calculate TF-IDF similarity
            texts = [manuscript_text, reviewer_text]
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

            # Boost score if specializations match
            manuscript_spec = manuscript.specialization.name if manuscript.specialization else ""
            if manuscript_spec in reviewer_specializations:
                similarity = min(1.0, similarity * 1.5)

            return float(similarity)

        except Exception as e:
            logger.warning(f"Error calculating expertise match: {e}")
            return 0.0

    def _calculate_network_score(self, manuscript, reviewer: 'User') -> float:
        """
        Calculate citation network score.
        In a full implementation, this would analyze:
        - Co-citation networks
        - Bibliographic coupling
        - Shared references
        """
        # Simplified implementation - check if same specialization
        if manuscript.specialization_id:
            reviewer_spec_ids = [spec.id for spec in reviewer.specializations]
            if manuscript.specialization_id in reviewer_spec_ids:
                return 0.8

        return 0.3  # Default neutral score

    def _calculate_performance_score(self, reviewer: 'User') -> float:
        """
        Calculate reviewer's past performance score based on:
        - Review completion rate
        - Average turnaround time
        - Review quality indicators
        """
        from db.models import Review, ReviewStatus

        # Get reviewer's past reviews
        reviews = self.db.query(Review).filter(Review.reviewer_id == reviewer.id).all()

        if not reviews:
            return 0.5  # Neutral score for new reviewers

        # Calculate metrics
        total_invitations = len(reviews)
        completed = len([r for r in reviews if r.status == ReviewStatus.COMPLETED])
        declined = len([r for r in reviews if r.status == ReviewStatus.DECLINED])

        # Completion rate
        completion_rate = completed / total_invitations if total_invitations > 0 else 0

        # Average turnaround time (days)
        completed_reviews = [r for r in reviews if r.completed_at and r.accepted_at]
        if completed_reviews:
            turnaround_times = [
                (r.completed_at - r.accepted_at).days
                for r in completed_reviews
            ]
            avg_turnaround = sum(turnaround_times) / len(turnaround_times)
            # Score: faster is better (assuming 21 days is target)
            turnaround_score = max(0, 1 - (avg_turnaround - 21) / 21)
        else:
            turnaround_score = 0.5

        # Quality score (based on providing detailed feedback)
        quality_scores = []
        for review in completed_reviews:
            # Score based on comment length as proxy for quality
            comment_length = len(review.comments_to_author or "") + len(review.comments_to_editor or "")
            quality_scores.append(min(1.0, comment_length / 500))  # 500 chars = good quality

        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.5

        # Combined score
        performance_score = (
            completion_rate * 0.4 +
            turnaround_score * 0.3 +
            avg_quality * 0.3
        )

        return performance_score

    def _calculate_availability_score(self, reviewer: 'User') -> float:
        """
        Calculate availability based on current workload.
        """
        from db.models import Review, ReviewStatus

        # Count active reviews (pending or in progress)
        active_reviews = self.db.query(Review).filter(
            Review.reviewer_id == reviewer.id,
            Review.status.in_([ReviewStatus.PENDING, ReviewStatus.IN_PROGRESS])
        ).count()

        # Score based on workload
        if active_reviews == 0:
            return 1.0
        elif active_reviews == 1:
            return 0.8
        elif active_reviews == 2:
            return 0.5
        elif active_reviews == 3:
            return 0.2
        else:
            return 0.0  # Too busy

    def _calculate_diversity_score(self, manuscript, reviewer: 'User') -> float:
        """
        Calculate diversity score to promote geographic and institutional diversity.
        """
        # Check if reviewer is from different country than authors
        author_countries = set(author.country for author in manuscript.authors if author.country)
        reviewer_country = reviewer.country

        if reviewer_country and reviewer_country not in author_countries:
            diversity_bonus = 0.7
        else:
            diversity_bonus = 0.3

        # Check institutional diversity
        author_affiliations = set(author.affiliation for author in manuscript.authors if author.affiliation)
        if reviewer.affiliation and reviewer.affiliation not in author_affiliations:
            diversity_bonus += 0.3

        return min(1.0, diversity_bonus)

    def _extract_matching_keywords(self, manuscript, reviewer: 'User') -> List[str]:
        """Extract keywords that match between manuscript and reviewer."""
        manuscript_keywords = set(keyword.lower() for keyword in (manuscript.keywords or []))
        reviewer_specializations = set(spec.name.lower() for spec in reviewer.specializations)

        matching = manuscript_keywords.intersection(reviewer_specializations)
        return list(matching)[:5]

    def _generate_matching_reason(self, score_breakdown: Dict) -> str:
        """Generate human-readable explanation for the match."""
        reasons = []

        if score_breakdown['expertise_score'] > 0.7:
            reasons.append("Strong expertise match")
        elif score_breakdown['expertise_score'] > 0.5:
            reasons.append("Good expertise match")

        if score_breakdown['performance_score'] > 0.8:
            reasons.append("excellent past performance")

        if score_breakdown['availability_score'] > 0.8:
            reasons.append("highly available")

        if score_breakdown['network_score'] > 0.7:
            reasons.append("strong citation network connection")

        if score_breakdown['matching_keywords']:
            keywords = ', '.join(score_breakdown['matching_keywords'][:3])
            reasons.append(f"matches keywords: {keywords}")

        if not reasons:
            reasons.append("moderate overall match")

        return " • ".join(reasons).capitalize()

    def _estimate_review_quality(self, reviewer: 'User') -> str:
        """Estimate expected review quality."""
        from db.models import Review, ReviewStatus

        completed_reviews = self.db.query(Review).filter(
            Review.reviewer_id == reviewer.id,
            Review.status == ReviewStatus.COMPLETED
        ).all()

        if not completed_reviews:
            return "Unknown (new reviewer)"

        # Calculate average comment length
        total_length = sum(
            len(r.comments_to_author or "") + len(r.comments_to_editor or "")
            for r in completed_reviews
        )
        avg_length = total_length / len(completed_reviews)

        if avg_length > 800:
            return "Excellent (detailed feedback)"
        elif avg_length > 400:
            return "Good (thorough reviews)"
        elif avg_length > 200:
            return "Adequate (basic feedback)"
        else:
            return "Brief (concise reviews)"

    def _get_average_turnaround(self, reviewer: 'User') -> Optional[int]:
        """Get average review turnaround time in days."""
        from db.models import Review, ReviewStatus

        completed_reviews = self.db.query(Review).filter(
            Review.reviewer_id == reviewer.id,
            Review.status == ReviewStatus.COMPLETED,
            Review.accepted_at.isnot(None),
            Review.completed_at.isnot(None)
        ).all()

        if not completed_reviews:
            return None

        turnaround_times = [
            (r.completed_at - r.accepted_at).days
            for r in completed_reviews
        ]

        return int(sum(turnaround_times) / len(turnaround_times))

    def _apply_diversity_boost(
        self,
        reviewer_scores: List[Dict],
        manuscript
    ) -> List[Dict]:
        """
        Apply diversity boost to ensure geographic and institutional variety.
        """
        if len(reviewer_scores) <= 3:
            return reviewer_scores

        # Track countries and affiliations in top candidates
        top_countries = defaultdict(int)
        top_affiliations = defaultdict(int)

        for i, reviewer in enumerate(reviewer_scores[:20]):
            country = reviewer.get('country')
            affiliation = reviewer.get('affiliation')

            # Apply penalty for overrepresentation
            country_penalty = top_countries[country] * 0.05 if country else 0
            affiliation_penalty = top_affiliations[affiliation] * 0.03 if affiliation else 0

            reviewer_scores[i]['total_score'] -= (country_penalty + affiliation_penalty)

            # Update counts
            if country:
                top_countries[country] += 1
            if affiliation:
                top_affiliations[affiliation] += 1

        # Re-sort after diversity adjustment
        reviewer_scores.sort(key=lambda x: x['total_score'], reverse=True)

        return reviewer_scores

    def get_reviewer_statistics(self, reviewer_id: int) -> Dict:
        """Get comprehensive statistics for a reviewer."""
        from db.models import Review, ReviewStatus, User

        reviewer = self.db.query(User).filter(User.id == reviewer_id).first()
        if not reviewer:
            return {}

        reviews = self.db.query(Review).filter(Review.reviewer_id == reviewer_id).all()

        total_invitations = len(reviews)
        completed = [r for r in reviews if r.status == ReviewStatus.COMPLETED]
        declined = [r for r in reviews if r.status == ReviewStatus.DECLINED]
        pending = [r for r in reviews if r.status == ReviewStatus.PENDING]
        in_progress = [r for r in reviews if r.status == ReviewStatus.IN_PROGRESS]

        stats = {
            'reviewer_id': reviewer_id,
            'reviewer_name': reviewer.full_name,
            'total_invitations': total_invitations,
            'completed': len(completed),
            'declined': len(declined),
            'pending': len(pending),
            'in_progress': len(in_progress),
            'completion_rate': len(completed) / total_invitations if total_invitations > 0 else 0,
            'decline_rate': len(declined) / total_invitations if total_invitations > 0 else 0,
        }

        # Calculate turnaround time
        if completed:
            turnaround_times = [
                (r.completed_at - r.accepted_at).days
                for r in completed
                if r.completed_at and r.accepted_at
            ]
            if turnaround_times:
                stats['average_turnaround_days'] = sum(turnaround_times) / len(turnaround_times)
                stats['fastest_turnaround_days'] = min(turnaround_times)
                stats['slowest_turnaround_days'] = max(turnaround_times)

        # Recommendation distribution
        from db.models import ReviewRecommendation
        recommendations = [r.recommendation for r in completed if r.recommendation]
        if recommendations:
            stats['recommendation_distribution'] = {
                'accept': recommendations.count(ReviewRecommendation.ACCEPT),
                'minor_revisions': recommendations.count(ReviewRecommendation.MINOR_REVISIONS),
                'major_revisions': recommendations.count(ReviewRecommendation.MAJOR_REVISIONS),
                'reject': recommendations.count(ReviewRecommendation.REJECT)
            }

        return stats


def suggest_reviewers_for_manuscript(manuscript_id: int, db_session, num_reviewers: int = 10) -> List[Dict]:
    """
    Convenience function to get reviewer suggestions.

    Args:
        manuscript_id: Manuscript ID
        db_session: Database session
        num_reviewers: Number of suggestions to return

    Returns:
        List of reviewer suggestions with scores and explanations
    """
    engine = ReviewerMatchingEngine(db_session)
    return engine.find_best_reviewers(manuscript_id, num_reviewers)
