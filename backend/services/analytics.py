"""
Advanced Analytics and Business Intelligence Dashboard

Provides comprehensive metrics, insights, and reporting for journal management.
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_, case, distinct
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


class AnalyticsDashboard:
    """
    Comprehensive analytics engine for journal metrics and insights.
    """

    def __init__(self, db_session: Session):
        self.db = db_session

    def get_overview_metrics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get high-level overview metrics for dashboard.

        Args:
            days: Number of days to look back for trends

        Returns:
            Dictionary with key metrics and trends
        """
        from db.models import Manuscript, Review, User, ManuscriptStatus, ReviewStatus

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Total manuscripts by status
        total_manuscripts = self.db.query(Manuscript).count()
        submitted_count = self.db.query(Manuscript).filter(
            Manuscript.status == ManuscriptStatus.SUBMITTED
        ).count()
        under_review_count = self.db.query(Manuscript).filter(
            Manuscript.status == ManuscriptStatus.UNDER_REVIEW
        ).count()
        accepted_count = self.db.query(Manuscript).filter(
            Manuscript.status == ManuscriptStatus.ACCEPTED
        ).count()
        published_count = self.db.query(Manuscript).filter(
            Manuscript.status == ManuscriptStatus.PUBLISHED
        ).count()

        # Recent submissions
        recent_submissions = self.db.query(Manuscript).filter(
            Manuscript.submitted_at >= cutoff_date
        ).count()

        # Active reviews
        active_reviews = self.db.query(Review).filter(
            Review.status.in_([ReviewStatus.PENDING, ReviewStatus.IN_PROGRESS])
        ).count()

        # Completed reviews
        completed_reviews = self.db.query(Review).filter(
            Review.status == ReviewStatus.COMPLETED,
            Review.completed_at >= cutoff_date
        ).count()

        # User counts
        total_users = self.db.query(User).filter(User.is_active == True).count()

        # Calculate trends
        previous_cutoff = datetime.utcnow() - timedelta(days=days*2)
        previous_submissions = self.db.query(Manuscript).filter(
            Manuscript.submitted_at >= previous_cutoff,
            Manuscript.submitted_at < cutoff_date
        ).count()

        submission_trend = self._calculate_trend(recent_submissions, previous_submissions)

        return {
            'total_manuscripts': total_manuscripts,
            'submitted': submitted_count,
            'under_review': under_review_count,
            'accepted': accepted_count,
            'published': published_count,
            'recent_submissions': recent_submissions,
            'submission_trend': submission_trend,
            'active_reviews': active_reviews,
            'completed_reviews': completed_reviews,
            'total_users': total_users,
            'acceptance_rate': self._calculate_acceptance_rate(),
            'average_review_time': self._calculate_average_review_time(),
            'time_to_first_decision': self._calculate_time_to_first_decision()
        }

    def get_submission_analytics(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict:
        """Get detailed submission analytics."""
        from db.models import Manuscript, ManuscriptStatus

        query = self.db.query(Manuscript)

        if start_date:
            query = query.filter(Manuscript.submitted_at >= start_date)
        if end_date:
            query = query.filter(Manuscript.submitted_at <= end_date)

        manuscripts = query.all()

        # Submissions by month
        submissions_by_month = self._group_by_month(manuscripts, 'submitted_at')

        # Submissions by specialization
        submissions_by_specialization = self.db.query(
            Manuscript.specialization_id,
            func.count(Manuscript.id)
        ).group_by(Manuscript.specialization_id).all()

        # Geographic distribution (by author country)
        geographic_dist = self._get_geographic_distribution()

        # Article types distribution
        article_types = self.db.query(
            Manuscript.article_type,
            func.count(Manuscript.id)
        ).filter(
            Manuscript.article_type.isnot(None)
        ).group_by(Manuscript.article_type).all()

        return {
            'total_submissions': len(manuscripts),
            'submissions_by_month': submissions_by_month,
            'submissions_by_specialization': dict(submissions_by_specialization),
            'geographic_distribution': geographic_dist,
            'article_types': dict(article_types),
            'average_authors_per_paper': self._calculate_avg_authors(),
            'manuscripts_with_revisions': self._count_manuscripts_with_revisions()
        }

    def get_review_analytics(self) -> Dict:
        """Get detailed review process analytics."""
        from db.models import Review, ReviewStatus, ReviewRecommendation

        # Total reviews
        total_reviews = self.db.query(Review).count()

        # Reviews by status
        reviews_by_status = self.db.query(
            Review.status,
            func.count(Review.id)
        ).group_by(Review.status).all()

        # Average review time
        completed_reviews = self.db.query(Review).filter(
            Review.status == ReviewStatus.COMPLETED,
            Review.accepted_at.isnot(None),
            Review.completed_at.isnot(None)
        ).all()

        if completed_reviews:
            review_times = [(r.completed_at - r.accepted_at).days for r in completed_reviews]
            avg_review_time = sum(review_times) / len(review_times)
            min_review_time = min(review_times)
            max_review_time = max(review_times)
        else:
            avg_review_time = min_review_time = max_review_time = None

        # Reviewer acceptance rate
        total_invitations = self.db.query(Review).count()
        accepted_invitations = self.db.query(Review).filter(
            Review.status.in_([ReviewStatus.IN_PROGRESS, ReviewStatus.COMPLETED])
        ).count()
        acceptance_rate = accepted_invitations / total_invitations if total_invitations > 0 else 0

        # Recommendations distribution
        recommendations = self.db.query(
            Review.recommendation,
            func.count(Review.id)
        ).filter(
            Review.recommendation.isnot(None)
        ).group_by(Review.recommendation).all()

        # Top reviewers
        top_reviewers = self._get_top_reviewers(limit=10)

        # Review quality metrics
        quality_metrics = self._calculate_review_quality_metrics()

        return {
            'total_reviews': total_reviews,
            'reviews_by_status': dict(reviews_by_status),
            'average_review_time_days': avg_review_time,
            'min_review_time_days': min_review_time,
            'max_review_time_days': max_review_time,
            'reviewer_acceptance_rate': acceptance_rate,
            'recommendations_distribution': dict(recommendations),
            'top_reviewers': top_reviewers,
            'quality_metrics': quality_metrics
        }

    def get_publication_analytics(self) -> Dict:
        """Get publication metrics and trends."""
        from db.models import Manuscript, ManuscriptStatus

        # Total publications
        published = self.db.query(Manuscript).filter(
            Manuscript.status == ManuscriptStatus.PUBLISHED
        ).all()

        # Publications by month
        publications_by_month = self._group_by_month(published, 'published_at')

        # Time from submission to publication
        if published:
            pub_times = [
                (m.published_at - m.submitted_at).days
                for m in published
                if m.published_at and m.submitted_at
            ]
            if pub_times:
                avg_time_to_publication = sum(pub_times) / len(pub_times)
                min_time = min(pub_times)
                max_time = max(pub_times)
            else:
                avg_time_to_publication = min_time = max_time = None
        else:
            avg_time_to_publication = min_time = max_time = None

        # Articles with DOI
        articles_with_doi = self.db.query(Manuscript).filter(
            Manuscript.doi.isnot(None)
        ).count()

        # PMC submissions
        pmc_submissions = self.db.query(Manuscript).filter(
            Manuscript.submitted_to_pmc == True
        ).count()

        # Total views and downloads
        total_views = self.db.query(func.sum(Manuscript.views)).scalar() or 0
        total_downloads = self.db.query(func.sum(Manuscript.downloads)).scalar() or 0

        # Most viewed articles
        most_viewed = self.db.query(Manuscript).filter(
            Manuscript.status == ManuscriptStatus.PUBLISHED
        ).order_by(Manuscript.views.desc()).limit(10).all()

        return {
            'total_publications': len(published),
            'publications_by_month': publications_by_month,
            'average_time_to_publication_days': avg_time_to_publication,
            'min_time_to_publication_days': min_time,
            'max_time_to_publication_days': max_time,
            'articles_with_doi': articles_with_doi,
            'pmc_submissions': pmc_submissions,
            'total_views': total_views,
            'total_downloads': total_downloads,
            'average_views_per_article': total_views / len(published) if published else 0,
            'average_downloads_per_article': total_downloads / len(published) if published else 0,
            'most_viewed_articles': [
                {
                    'id': m.id,
                    'manuscript_id': m.manuscript_id,
                    'title': m.title,
                    'views': m.views,
                    'downloads': m.downloads
                }
                for m in most_viewed
            ]
        }

    def get_editorial_performance(self) -> Dict:
        """Get editorial team performance metrics."""
        from db.models import EditorialDecision, DecisionType, User, UserRole

        # Total decisions
        total_decisions = self.db.query(EditorialDecision).count()

        # Decisions by type
        decisions_by_type = self.db.query(
            EditorialDecision.decision,
            func.count(EditorialDecision.id)
        ).group_by(EditorialDecision.decision).all()

        # Most active editors
        active_editors = self.db.query(
            User.id,
            User.full_name,
            func.count(EditorialDecision.id).label('decision_count')
        ).join(
            EditorialDecision,
            User.id == EditorialDecision.editor_id
        ).group_by(User.id, User.full_name).order_by(
            func.count(EditorialDecision.id).desc()
        ).limit(10).all()

        # Average time to decision
        avg_decision_time = self._calculate_time_to_first_decision()

        return {
            'total_decisions': total_decisions,
            'decisions_by_type': dict(decisions_by_type),
            'active_editors': [
                {'id': e[0], 'name': e[1], 'decisions': e[2]}
                for e in active_editors
            ],
            'average_time_to_decision_days': avg_decision_time
        }

    def get_user_analytics(self) -> Dict:
        """Get user statistics and demographics."""
        from db.models import User, UserRole

        # Total users by role
        users_by_role = self.db.query(
            User.role,
            func.count(User.id)
        ).filter(
            User.is_active == True
        ).group_by(User.role).all()

        # Geographic distribution
        users_by_country = self.db.query(
            User.country,
            func.count(User.id)
        ).filter(
            User.country.isnot(None),
            User.is_active == True
        ).group_by(User.country).order_by(
            func.count(User.id).desc()
        ).limit(20).all()

        # Users with ORCID
        users_with_orcid = self.db.query(User).filter(
            User.orcid.isnot(None),
            User.is_active == True
        ).count()

        # Recently registered users
        recent_registrations = self.db.query(User).filter(
            User.created_at >= datetime.utcnow() - timedelta(days=30),
            User.is_active == True
        ).count()

        return {
            'users_by_role': dict(users_by_role),
            'users_by_country': dict(users_by_country),
            'total_active_users': self.db.query(User).filter(User.is_active == True).count(),
            'users_with_orcid': users_with_orcid,
            'recent_registrations_30d': recent_registrations
        }

    def generate_custom_report(
        self,
        report_type: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        filters: Optional[Dict] = None
    ) -> Dict:
        """
        Generate custom reports based on type and filters.

        Report types:
        - manuscript_flow: Manuscript workflow analysis
        - reviewer_performance: Detailed reviewer metrics
        - publication_summary: Publication statistics
        - financial: Financial metrics (for hybrid OA)
        - geographic: Geographic distribution analysis
        """
        if report_type == 'manuscript_flow':
            return self._generate_manuscript_flow_report(start_date, end_date, filters)
        elif report_type == 'reviewer_performance':
            return self._generate_reviewer_performance_report(start_date, end_date, filters)
        elif report_type == 'publication_summary':
            return self._generate_publication_summary_report(start_date, end_date, filters)
        elif report_type == 'geographic':
            return self._generate_geographic_report(start_date, end_date, filters)
        else:
            raise ValueError(f"Unknown report type: {report_type}")

    # Helper methods

    def _calculate_trend(self, current: int, previous: int) -> float:
        """Calculate percentage trend."""
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return ((current - previous) / previous) * 100

    def _calculate_acceptance_rate(self) -> float:
        """Calculate overall acceptance rate."""
        from db.models import Manuscript, ManuscriptStatus

        total_decided = self.db.query(Manuscript).filter(
            Manuscript.status.in_([
                ManuscriptStatus.ACCEPTED,
                ManuscriptStatus.REJECTED,
                ManuscriptStatus.PUBLISHED
            ])
        ).count()

        accepted = self.db.query(Manuscript).filter(
            Manuscript.status.in_([
                ManuscriptStatus.ACCEPTED,
                ManuscriptStatus.PUBLISHED
            ])
        ).count()

        return accepted / total_decided if total_decided > 0 else 0

    def _calculate_average_review_time(self) -> Optional[float]:
        """Calculate average review time in days."""
        from db.models import Review, ReviewStatus

        completed_reviews = self.db.query(Review).filter(
            Review.status == ReviewStatus.COMPLETED,
            Review.accepted_at.isnot(None),
            Review.completed_at.isnot(None)
        ).all()

        if not completed_reviews:
            return None

        review_times = [(r.completed_at - r.accepted_at).days for r in completed_reviews]
        return sum(review_times) / len(review_times)

    def _calculate_time_to_first_decision(self) -> Optional[float]:
        """Calculate average time from submission to first decision."""
        from db.models import Manuscript, EditorialDecision

        manuscripts_with_decisions = self.db.query(Manuscript).join(
            EditorialDecision
        ).filter(
            Manuscript.submitted_at.isnot(None)
        ).all()

        if not manuscripts_with_decisions:
            return None

        decision_times = []
        for manuscript in manuscripts_with_decisions:
            if manuscript.decisions:
                first_decision = min(manuscript.decisions, key=lambda d: d.decided_at)
                days = (first_decision.decided_at - manuscript.submitted_at).days
                decision_times.append(days)

        return sum(decision_times) / len(decision_times) if decision_times else None

    def _group_by_month(self, items: List, date_field: str) -> Dict:
        """Group items by month."""
        from collections import defaultdict

        by_month = defaultdict(int)

        for item in items:
            date_value = getattr(item, date_field, None)
            if date_value:
                month_key = date_value.strftime('%Y-%m')
                by_month[month_key] += 1

        return dict(sorted(by_month.items()))

    def _get_geographic_distribution(self) -> Dict:
        """Get geographic distribution of submissions."""
        from db.models import Manuscript, manuscript_authors, User

        country_counts = self.db.query(
            User.country,
            func.count(distinct(Manuscript.id))
        ).join(
            manuscript_authors,
            User.id == manuscript_authors.c.author_id
        ).join(
            Manuscript,
            manuscript_authors.c.manuscript_id == Manuscript.id
        ).filter(
            User.country.isnot(None)
        ).group_by(User.country).order_by(
            func.count(distinct(Manuscript.id)).desc()
        ).limit(20).all()

        return dict(country_counts)

    def _calculate_avg_authors(self) -> float:
        """Calculate average number of authors per manuscript."""
        from db.models import Manuscript, manuscript_authors

        author_counts = self.db.query(
            Manuscript.id,
            func.count(manuscript_authors.c.author_id)
        ).join(
            manuscript_authors,
            Manuscript.id == manuscript_authors.c.manuscript_id
        ).group_by(Manuscript.id).all()

        if not author_counts:
            return 0

        total_authors = sum(count for _, count in author_counts)
        return total_authors / len(author_counts)

    def _count_manuscripts_with_revisions(self) -> int:
        """Count manuscripts that went through revisions."""
        from db.models import Manuscript

        return self.db.query(Manuscript).filter(
            Manuscript.version > 1
        ).count()

    def _get_top_reviewers(self, limit: int = 10) -> List[Dict]:
        """Get top reviewers by number of completed reviews."""
        from db.models import Review, ReviewStatus, User

        top_reviewers = self.db.query(
            User.id,
            User.full_name,
            User.affiliation,
            func.count(Review.id).label('review_count')
        ).join(
            Review,
            User.id == Review.reviewer_id
        ).filter(
            Review.status == ReviewStatus.COMPLETED
        ).group_by(User.id, User.full_name, User.affiliation).order_by(
            func.count(Review.id).desc()
        ).limit(limit).all()

        return [
            {
                'id': r[0],
                'name': r[1],
                'affiliation': r[2],
                'completed_reviews': r[3]
            }
            for r in top_reviewers
        ]

    def _calculate_review_quality_metrics(self) -> Dict:
        """Calculate review quality indicators."""
        from db.models import Review, ReviewStatus

        completed = self.db.query(Review).filter(
            Review.status == ReviewStatus.COMPLETED
        ).all()

        if not completed:
            return {}

        # Average comment length
        comment_lengths = [
            len(r.comments_to_author or "") + len(r.comments_to_editor or "")
            for r in completed
        ]
        avg_comment_length = sum(comment_lengths) / len(comment_lengths)

        # Reviews with scores
        reviews_with_scores = len([
            r for r in completed
            if r.score_originality and r.score_methodology
        ])

        return {
            'average_comment_length': avg_comment_length,
            'reviews_with_detailed_scores': reviews_with_scores,
            'review_completion_rate': len(completed) / self.db.query(Review).count()
        }

    def _generate_manuscript_flow_report(
        self,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        filters: Optional[Dict]
    ) -> Dict:
        """Generate manuscript flow analysis report."""
        # Implementation would provide detailed workflow analysis
        return {
            'report_type': 'manuscript_flow',
            'generated_at': datetime.utcnow().isoformat(),
            'date_range': {
                'start': start_date.isoformat() if start_date else None,
                'end': end_date.isoformat() if end_date else None
            },
            'data': {
                'workflow_stages': self._analyze_workflow_stages(),
                'bottlenecks': self._identify_bottlenecks(),
                'average_times': self._calculate_stage_times()
            }
        }

    def _generate_reviewer_performance_report(
        self,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        filters: Optional[Dict]
    ) -> Dict:
        """Generate detailed reviewer performance report."""
        from services.reviewer_matching import ReviewerMatchingEngine

        engine = ReviewerMatchingEngine(self.db)

        # Get all reviewers with statistics
        from db.models import User, UserRole
        reviewers = self.db.query(User).filter(User.role == UserRole.REVIEWER).all()

        reviewer_stats = []
        for reviewer in reviewers:
            stats = engine.get_reviewer_statistics(reviewer.id)
            if stats:
                reviewer_stats.append(stats)

        return {
            'report_type': 'reviewer_performance',
            'generated_at': datetime.utcnow().isoformat(),
            'total_reviewers': len(reviewers),
            'reviewer_statistics': reviewer_stats
        }

    def _generate_publication_summary_report(
        self,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        filters: Optional[Dict]
    ) -> Dict:
        """Generate publication summary report."""
        return {
            'report_type': 'publication_summary',
            'generated_at': datetime.utcnow().isoformat(),
            'data': self.get_publication_analytics()
        }

    def _generate_geographic_report(
        self,
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        filters: Optional[Dict]
    ) -> Dict:
        """Generate geographic distribution report."""
        return {
            'report_type': 'geographic',
            'generated_at': datetime.utcnow().isoformat(),
            'data': {
                'author_distribution': self._get_geographic_distribution(),
                'reviewer_distribution': self._get_reviewer_geographic_distribution(),
                'collaboration_network': self._analyze_international_collaboration()
            }
        }

    def _analyze_workflow_stages(self) -> Dict:
        """Analyze manuscripts in each workflow stage."""
        from db.models import Manuscript, ManuscriptStatus

        stages = {}
        for status in ManuscriptStatus:
            count = self.db.query(Manuscript).filter(
                Manuscript.status == status
            ).count()
            stages[status.value] = count

        return stages

    def _identify_bottlenecks(self) -> List[Dict]:
        """Identify workflow bottlenecks."""
        # Simplified implementation
        return []

    def _calculate_stage_times(self) -> Dict:
        """Calculate average time spent in each stage."""
        # Simplified implementation
        return {}

    def _get_reviewer_geographic_distribution(self) -> Dict:
        """Get geographic distribution of reviewers."""
        from db.models import User, UserRole

        dist = self.db.query(
            User.country,
            func.count(User.id)
        ).filter(
            User.role == UserRole.REVIEWER,
            User.country.isnot(None)
        ).group_by(User.country).all()

        return dict(dist)

    def _analyze_international_collaboration(self) -> Dict:
        """Analyze international collaboration patterns."""
        # Simplified implementation
        return {'total_collaborations': 0, 'countries_involved': []}
