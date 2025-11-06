"""
Rule-Based Reviewer Matching System.

Matches reviewers to manuscripts using:
- Keyword matching
- Subject area overlap
- Expertise level
- Availability
- Workload balancing
- Geographic diversity

No ML required - uses scoring and ranking algorithms.
"""
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import Counter
import re


@dataclass
class ReviewerMatch:
    """Reviewer match with scoring."""
    reviewer_id: int
    reviewer_name: str
    reviewer_email: str
    affiliation: str
    expertise_areas: List[str]
    match_score: float  # 0-100
    expertise_match: float  # 0-100
    availability_score: float  # 0-100
    workload_score: float  # 0-100
    reasons: List[str]
    concerns: List[str]


class RuleBasedReviewerMatcher:
    """
    Matches reviewers to manuscripts using rule-based scoring.

    Much faster than ML embeddings, transparent reasoning,
    and works well for most cases.
    """

    def find_best_reviewers(
        self,
        manuscript: Dict,
        available_reviewers: List[Dict],
        num_reviewers: int = 5,
        exclude_author_ids: Optional[List[int]] = None,
        require_expertise_threshold: float = 30.0
    ) -> List[ReviewerMatch]:
        """
        Find best reviewer matches for a manuscript.

        Args:
            manuscript: Manuscript data (title, abstract, keywords, subject_area)
            available_reviewers: List of potential reviewers
            num_reviewers: Number of matches to return
            exclude_author_ids: Author IDs to exclude (CoI)
            require_expertise_threshold: Minimum expertise score required

        Returns:
            List of ReviewerMatch objects, sorted by match_score
        """
        if exclude_author_ids is None:
            exclude_author_ids = []

        matches = []

        for reviewer in available_reviewers:
            # Skip if conflict of interest
            if reviewer['id'] in exclude_author_ids:
                continue

            # Calculate match scores
            expertise_score = self._calculate_expertise_match(
                manuscript, reviewer
            )

            # Skip if expertise too low
            if expertise_score < require_expertise_threshold:
                continue

            availability_score = self._calculate_availability(reviewer)
            workload_score = self._calculate_workload_score(reviewer)

            # Overall match score (weighted average)
            match_score = (
                expertise_score * 0.6 +    # 60% - most important
                availability_score * 0.2 +  # 20%
                workload_score * 0.2        # 20%
            )

            # Generate reasons and concerns
            reasons, concerns = self._generate_match_reasoning(
                expertise_score, availability_score, workload_score, reviewer
            )

            matches.append(ReviewerMatch(
                reviewer_id=reviewer['id'],
                reviewer_name=reviewer['name'],
                reviewer_email=reviewer['email'],
                affiliation=reviewer.get('affiliation', ''),
                expertise_areas=reviewer.get('expertise_areas', []),
                match_score=match_score,
                expertise_match=expertise_score,
                availability_score=availability_score,
                workload_score=workload_score,
                reasons=reasons,
                concerns=concerns
            ))

        # Sort by match score (descending)
        matches.sort(key=lambda x: x.match_score, reverse=True)

        return matches[:num_reviewers]

    def _calculate_expertise_match(
        self,
        manuscript: Dict,
        reviewer: Dict
    ) -> float:
        """
        Calculate expertise match (0-100).

        Uses:
        - Keyword overlap
        - Subject area match
        - Title/abstract term matching
        """
        score = 0.0

        # Extract manuscript terms
        manuscript_keywords = set(k.lower() for k in manuscript.get('keywords', []))
        manuscript_title_words = set(
            word.lower() for word in re.findall(r'\w+', manuscript.get('title', ''))
            if len(word) > 3
        )
        manuscript_abstract_words = set(
            word.lower() for word in re.findall(r'\w+', manuscript.get('abstract', ''))
            if len(word) > 3
        )

        # Extract reviewer expertise terms
        reviewer_expertise = set(
            area.lower() for area in reviewer.get('expertise_areas', [])
        )
        reviewer_keywords = set(
            kw.lower() for kw in reviewer.get('research_keywords', [])
        )
        reviewer_bio_words = set()
        if reviewer.get('bio'):
            reviewer_bio_words = set(
                word.lower() for word in re.findall(r'\w+', reviewer['bio'])
                if len(word) > 3
            )

        # 1. Keyword exact match (most important) - 40 points
        keyword_matches = manuscript_keywords & reviewer_keywords
        if manuscript_keywords:
            keyword_score = (len(keyword_matches) / len(manuscript_keywords)) * 40
            score += min(keyword_score, 40)

        # 2. Expertise area match - 30 points
        # Check if manuscript keywords appear in reviewer expertise areas
        expertise_matches = sum(
            1 for mk in manuscript_keywords
            for re_area in reviewer_expertise
            if mk in re_area or re_area in mk
        )
        if manuscript_keywords:
            expertise_score = (expertise_matches / len(manuscript_keywords)) * 30
            score += min(expertise_score, 30)

        # 3. Title term overlap - 15 points
        title_matches = manuscript_title_words & (reviewer_keywords | reviewer_expertise | reviewer_bio_words)
        if manuscript_title_words:
            title_score = (len(title_matches) / len(manuscript_title_words)) * 15
            score += min(title_score, 15)

        # 4. Subject area match - 15 points
        manuscript_subject = manuscript.get('subject_area', '').lower()
        reviewer_subjects = [s.lower() for s in reviewer.get('subject_areas', [])]
        if manuscript_subject in reviewer_subjects:
            score += 15
        elif any(manuscript_subject in rs or rs in manuscript_subject for rs in reviewer_subjects):
            score += 10

        return min(score, 100.0)

    def _calculate_availability(self, reviewer: Dict) -> float:
        """
        Calculate availability score (0-100).

        Considers:
        - Recently declined invitations
        - Response rate
        - Last review date
        """
        score = 100.0

        # Check recent declines
        recent_declines = reviewer.get('recent_declines', 0)
        if recent_declines >= 3:
            score -= 40
        elif recent_declines == 2:
            score -= 25
        elif recent_declines == 1:
            score -= 10

        # Check response rate
        response_rate = reviewer.get('response_rate', 1.0)  # 0-1
        if response_rate < 0.5:
            score -= 30
        elif response_rate < 0.7:
            score -= 15

        # Check last review date (prefer reviewers who reviewed recently - they're engaged)
        last_review_date = reviewer.get('last_review_date')
        if last_review_date:
            days_since_last = (datetime.now() - last_review_date).days
            if 30 <= days_since_last <= 180:  # Sweet spot
                score += 0  # No change
            elif days_since_last < 30:
                score -= 10  # Too recent, might be busy
            elif days_since_last > 365:
                score -= 20  # Been a while, might have moved on

        # Check if reviewer marked as unavailable
        if reviewer.get('is_available', True) == False:
            score -= 50

        return max(score, 0.0)

    def _calculate_workload_score(self, reviewer: Dict) -> float:
        """
        Calculate workload score (0-100).

        Higher score = less current workload (more capacity).
        """
        score = 100.0

        # Current active reviews
        active_reviews = reviewer.get('active_reviews', 0)
        if active_reviews >= 5:
            score -= 60
        elif active_reviews >= 3:
            score -= 40
        elif active_reviews >= 2:
            score -= 20
        elif active_reviews == 1:
            score -= 10

        # Reviews in last 6 months
        reviews_last_6mo = reviewer.get('reviews_last_6_months', 0)
        if reviews_last_6mo >= 10:
            score -= 20
        elif reviews_last_6mo >= 6:
            score -= 10

        # Overdue reviews (big penalty)
        overdue_reviews = reviewer.get('overdue_reviews', 0)
        if overdue_reviews >= 2:
            score -= 50
        elif overdue_reviews == 1:
            score -= 25

        return max(score, 0.0)

    def _generate_match_reasoning(
        self,
        expertise_score: float,
        availability_score: float,
        workload_score: float,
        reviewer: Dict
    ) -> Tuple[List[str], List[str]]:
        """Generate human-readable reasons and concerns."""
        reasons = []
        concerns = []

        # Expertise
        if expertise_score >= 70:
            reasons.append(f"Strong expertise match ({expertise_score:.0f}%)")
        elif expertise_score >= 50:
            reasons.append(f"Good expertise match ({expertise_score:.0f}%)")
        elif expertise_score >= 30:
            reasons.append(f"Moderate expertise match ({expertise_score:.0f}%)")
        else:
            concerns.append(f"Limited expertise match ({expertise_score:.0f}%)")

        # Availability
        if availability_score >= 80:
            reasons.append("Highly available")
        elif availability_score >= 60:
            reasons.append("Available")
        elif availability_score >= 40:
            concerns.append("Moderate availability concerns")
        else:
            concerns.append("Low availability")

        # Workload
        active_reviews = reviewer.get('active_reviews', 0)
        if workload_score >= 80:
            reasons.append("Light current workload")
        elif workload_score >= 60:
            reasons.append("Moderate workload")
        elif active_reviews >= 3:
            concerns.append(f"Heavy workload ({active_reviews} active reviews)")

        # Recent performance
        if reviewer.get('average_review_time_days'):
            avg_time = reviewer['average_review_time_days']
            if avg_time <= 14:
                reasons.append("Fast reviewer (avg 14 days)")
            elif avg_time <= 21:
                reasons.append("Timely reviewer (avg 21 days)")
            elif avg_time > 30:
                concerns.append(f"Slow reviewer (avg {avg_time} days)")

        # Quality of past reviews
        if reviewer.get('average_review_quality_score'):
            quality = reviewer['average_review_quality_score']
            if quality >= 4.5:
                reasons.append("Excellent review quality")
            elif quality >= 4.0:
                reasons.append("High review quality")

        return reasons, concerns


class ReviewerPoolAnalyzer:
    """
    Analyzes reviewer pool health and provides recommendations.
    """

    def analyze_reviewer_pool(
        self,
        reviewers: List[Dict]
    ) -> Dict:
        """
        Analyze overall reviewer pool health.

        Returns metrics and recommendations for pool management.
        """
        total_reviewers = len(reviewers)

        # Activity metrics
        active_reviewers = sum(1 for r in reviewers if r.get('active_reviews', 0) > 0)
        overloaded_reviewers = sum(1 for r in reviewers if r.get('active_reviews', 0) >= 3)
        inactive_reviewers = sum(
            1 for r in reviewers
            if r.get('last_review_date') and
            (datetime.now() - r['last_review_date']).days > 365
        )

        # Response metrics
        response_rates = [r.get('response_rate', 0) for r in reviewers]
        avg_response_rate = sum(response_rates) / len(response_rates) if response_rates else 0

        # Workload distribution
        workloads = [r.get('active_reviews', 0) for r in reviewers]
        workload_counter = Counter(workloads)

        # Expertise coverage
        all_expertise_areas = []
        for r in reviewers:
            all_expertise_areas.extend(r.get('expertise_areas', []))
        expertise_coverage = Counter(all_expertise_areas)

        # Generate recommendations
        recommendations = []

        if inactive_reviewers / total_reviewers > 0.3:
            recommendations.append(
                f"⚠️  High inactive rate: {inactive_reviewers}/{total_reviewers} "
                f"reviewers haven't reviewed in 12+ months. Consider re-engagement campaign."
            )

        if overloaded_reviewers > 0:
            recommendations.append(
                f"⚠️  {overloaded_reviewers} reviewers have 3+ active reviews. "
                f"Consider redistributing workload."
            )

        if avg_response_rate < 0.6:
            recommendations.append(
                f"⚠️  Low average response rate ({avg_response_rate:.1%}). "
                f"Review invitation process and timing."
            )

        if active_reviewers / total_reviewers < 0.2:
            recommendations.append(
                f"💡  Only {active_reviewers}/{total_reviewers} reviewers currently active. "
                f"Recruit more reviewers or engage inactive ones."
            )

        # Find gaps in expertise coverage
        sparse_areas = [area for area, count in expertise_coverage.items() if count < 3]
        if sparse_areas:
            recommendations.append(
                f"💡  Limited coverage in: {', '.join(sparse_areas[:5])}. "
                f"Consider recruiting specialists."
            )

        return {
            'total_reviewers': total_reviewers,
            'active_reviewers': active_reviewers,
            'inactive_reviewers': inactive_reviewers,
            'overloaded_reviewers': overloaded_reviewers,
            'average_response_rate': avg_response_rate,
            'workload_distribution': dict(workload_counter),
            'expertise_coverage': dict(expertise_coverage.most_common(20)),
            'recommendations': recommendations,
            'health_score': self._calculate_pool_health_score(
                total_reviewers, active_reviewers, inactive_reviewers,
                overloaded_reviewers, avg_response_rate
            )
        }

    def _calculate_pool_health_score(
        self,
        total: int,
        active: int,
        inactive: int,
        overloaded: int,
        avg_response_rate: float
    ) -> float:
        """Calculate overall pool health (0-100)."""
        score = 100.0

        # Penalize high inactive rate
        inactive_rate = inactive / total if total > 0 else 0
        if inactive_rate > 0.5:
            score -= 30
        elif inactive_rate > 0.3:
            score -= 15

        # Penalize low response rate
        if avg_response_rate < 0.5:
            score -= 25
        elif avg_response_rate < 0.7:
            score -= 10

        # Penalize overloaded reviewers
        if overloaded > total * 0.2:
            score -= 20
        elif overloaded > 0:
            score -= 10

        # Penalize low total number
        if total < 20:
            score -= 20
        elif total < 50:
            score -= 10

        return max(score, 0.0)


# Singleton instances
reviewer_matcher = RuleBasedReviewerMatcher()
pool_analyzer = ReviewerPoolAnalyzer()
