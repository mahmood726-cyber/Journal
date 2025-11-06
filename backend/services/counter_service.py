"""
COUNTER R5 compliant statistics tracking service.

Implements COUNTER Code of Practice Release 5 for article metrics.
Reference: https://www.projectcounter.org/code-of-practice-five-sections/
"""
from typing import List, Dict, Optional
from datetime import datetime, date, timedelta
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, extract
import json
from user_agents import parse as parse_user_agent

from ..db.models import Manuscript
from ..db.models_metrics import (
    ArticleMetricEvent,
    ArticleMetricSummary,
    JournalMetricSummary,
    EventType
)
from .llm_service import get_llm_service


class MetricEventRequest(BaseModel):
    """Request to track a metric event."""
    manuscript_id: int
    event_type: str
    user_id: Optional[int] = None
    session_id: str
    ip_address: str
    user_agent: str
    referrer: Optional[str] = None
    country_code: Optional[str] = None


class ArticleMetrics(BaseModel):
    """Article metrics summary."""
    manuscript_id: int
    title: str
    total_views: int
    unique_views: int
    total_downloads: int
    unique_downloads: int
    abstract_views: int
    full_text_views: int
    pdf_downloads: int
    xml_downloads: int
    top_countries: Dict[str, int]
    trend: str  # "increasing", "stable", "decreasing"


class COUNTERReport(BaseModel):
    """COUNTER R5 compliant report."""
    report_type: str  # TR_J1, TR_J4, etc.
    report_period_start: date
    report_period_end: date
    institution_name: str
    articles: List[Dict]
    total_records: int
    generated_at: datetime


class ArticleInsights(BaseModel):
    """AI-generated insights about article performance."""
    manuscript_id: int
    performance_summary: str
    interesting_patterns: List[str]
    recommendations: List[str]
    generated_at: datetime


class COUNTERService:
    """
    COUNTER R5 compliant statistics tracking service.

    Features:
    - Real-time event tracking
    - Bot filtering
    - Double-click filtering
    - Geographic tracking
    - COUNTER R5 report generation
    - AI-powered insights
    """

    # Bot patterns (COUNTER R5 robot list)
    BOT_PATTERNS = [
        'bot', 'spider', 'crawler', 'scraper', 'http', 'curl', 'wget',
        'python', 'java', 'perl', 'ruby', 'go-http', 'axios', 'okhttp'
    ]

    # Double-click window (10 seconds per COUNTER R5)
    DOUBLE_CLICK_WINDOW = 10

    def __init__(self):
        """Initialize COUNTER service."""
        self.llm = get_llm_service()

    async def track_event(
        self,
        request: MetricEventRequest,
        db: Session
    ) -> bool:
        """
        Track a metric event with COUNTER R5 compliance.

        Args:
            request: Event tracking request
            db: Database session

        Returns:
            bool: True if event was tracked
        """
        # 1. Check if bot (filter out for COUNTER reports)
        is_robot = self._is_robot(request.user_agent)

        # 2. Check for double-click
        is_double_click = await self._is_double_click(
            manuscript_id=request.manuscript_id,
            event_type=request.event_type,
            session_id=request.session_id,
            db=db
        )

        # 3. Determine if unique event
        is_unique = await self._is_unique_event(
            manuscript_id=request.manuscript_id,
            event_type=request.event_type,
            session_id=request.session_id,
            event_date=date.today(),
            db=db
        )

        # 4. Categorize referrer
        referrer_category = self._categorize_referrer(request.referrer)

        # 5. Create event record
        event = ArticleMetricEvent(
            manuscript_id=request.manuscript_id,
            event_type=request.event_type,
            event_date=date.today(),
            event_timestamp=datetime.utcnow(),
            user_id=request.user_id,
            session_id=request.session_id,
            ip_address=request.ip_address,
            user_agent=request.user_agent,
            country_code=request.country_code,
            referrer=request.referrer,
            referrer_category=referrer_category,
            is_robot=is_robot,
            is_unique=is_unique,
            is_double_click=is_double_click
        )

        db.add(event)

        # 6. Update daily summary (async/background task in production)
        await self._update_daily_summary(
            manuscript_id=request.manuscript_id,
            metric_date=date.today(),
            db=db
        )

        db.commit()

        return True

    def _is_robot(self, user_agent: str) -> bool:
        """Check if user agent is a bot (COUNTER R5 robot filtering)."""
        if not user_agent:
            return True

        user_agent_lower = user_agent.lower()

        # Check against bot patterns
        for pattern in self.BOT_PATTERNS:
            if pattern in user_agent_lower:
                return True

        # Parse user agent
        try:
            ua = parse_user_agent(user_agent)
            if ua.is_bot:
                return True
        except:
            pass

        return False

    async def _is_double_click(
        self,
        manuscript_id: int,
        event_type: str,
        session_id: str,
        db: Session
    ) -> bool:
        """Check if event is a double-click (within 10 seconds)."""
        cutoff_time = datetime.utcnow() - timedelta(seconds=self.DOUBLE_CLICK_WINDOW)

        recent_event = db.query(ArticleMetricEvent).filter(
            ArticleMetricEvent.manuscript_id == manuscript_id,
            ArticleMetricEvent.event_type == event_type,
            ArticleMetricEvent.session_id == session_id,
            ArticleMetricEvent.event_timestamp >= cutoff_time
        ).first()

        return recent_event is not None

    async def _is_unique_event(
        self,
        manuscript_id: int,
        event_type: str,
        session_id: str,
        event_date: date,
        db: Session
    ) -> bool:
        """Check if this is the first event of this type for this session/date."""
        existing_event = db.query(ArticleMetricEvent).filter(
            ArticleMetricEvent.manuscript_id == manuscript_id,
            ArticleMetricEvent.event_type == event_type,
            ArticleMetricEvent.session_id == session_id,
            ArticleMetricEvent.event_date == event_date,
            ArticleMetricEvent.is_robot == False,
            ArticleMetricEvent.is_double_click == False
        ).first()

        return existing_event is None

    def _categorize_referrer(self, referrer: Optional[str]) -> str:
        """Categorize referrer for analytics."""
        if not referrer:
            return "direct"

        referrer_lower = referrer.lower()

        if any(s in referrer_lower for s in ['google', 'bing', 'yahoo', 'duckduckgo', 'baidu']):
            return "search_engine"
        elif any(s in referrer_lower for s in ['facebook', 'twitter', 'linkedin', 'reddit']):
            return "social_media"
        elif any(s in referrer_lower for s in ['scholar.google', 'pubmed', 'arxiv']):
            return "academic"
        else:
            return "other"

    async def _update_daily_summary(
        self,
        manuscript_id: int,
        metric_date: date,
        db: Session
    ):
        """Update or create daily summary for manuscript."""
        # Get or create summary
        summary = db.query(ArticleMetricSummary).filter(
            ArticleMetricSummary.manuscript_id == manuscript_id,
            ArticleMetricSummary.metric_date == metric_date
        ).first()

        if not summary:
            summary = ArticleMetricSummary(
                manuscript_id=manuscript_id,
                metric_date=metric_date
            )
            db.add(summary)

        # Query events for this date (excluding bots and double-clicks)
        events = db.query(ArticleMetricEvent).filter(
            ArticleMetricEvent.manuscript_id == manuscript_id,
            ArticleMetricEvent.event_date == metric_date,
            ArticleMetricEvent.is_robot == False,
            ArticleMetricEvent.is_double_click == False
        ).all()

        # Calculate metrics
        summary.total_item_requests = sum(
            1 for e in events if e.event_type in [
                EventType.PDF_DOWNLOAD.value,
                EventType.XML_DOWNLOAD.value,
                EventType.HTML_VIEW.value
            ]
        )

        summary.unique_item_requests = sum(
            1 for e in events if e.event_type in [
                EventType.PDF_DOWNLOAD.value,
                EventType.XML_DOWNLOAD.value,
                EventType.HTML_VIEW.value
            ] and e.is_unique
        )

        summary.total_item_investigations = sum(
            1 for e in events if e.event_type in [
                EventType.ABSTRACT_VIEW.value,
                EventType.FULL_TEXT_VIEW.value,
                EventType.LANDING_PAGE_VIEW.value
            ]
        )

        summary.unique_item_investigations = sum(
            1 for e in events if e.event_type in [
                EventType.ABSTRACT_VIEW.value,
                EventType.FULL_TEXT_VIEW.value,
                EventType.LANDING_PAGE_VIEW.value
            ] and e.is_unique
        )

        # Breakdown by type
        summary.abstract_views = sum(1 for e in events if e.event_type == EventType.ABSTRACT_VIEW.value)
        summary.full_text_views = sum(1 for e in events if e.event_type == EventType.FULL_TEXT_VIEW.value)
        summary.pdf_downloads = sum(1 for e in events if e.event_type == EventType.PDF_DOWNLOAD.value)
        summary.xml_downloads = sum(1 for e in events if e.event_type == EventType.XML_DOWNLOAD.value)
        summary.html_views = sum(1 for e in events if e.event_type == EventType.HTML_VIEW.value)

        # Geographic breakdown
        countries = {}
        for event in events:
            if event.country_code:
                countries[event.country_code] = countries.get(event.country_code, 0) + 1
        summary.top_countries = json.dumps(countries)

        # Referrer breakdown
        referrers = {}
        for event in events:
            if event.referrer_category:
                referrers[event.referrer_category] = referrers.get(event.referrer_category, 0) + 1
        summary.referrer_breakdown = json.dumps(referrers)

        db.commit()

    async def get_article_metrics(
        self,
        manuscript_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        db: Session = None
    ) -> ArticleMetrics:
        """Get aggregated metrics for an article."""
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)

        # Get manuscript
        manuscript = db.query(Manuscript).filter(Manuscript.id == manuscript_id).first()

        # Query summaries
        summaries = db.query(ArticleMetricSummary).filter(
            ArticleMetricSummary.manuscript_id == manuscript_id,
            ArticleMetricSummary.metric_date >= start_date,
            ArticleMetricSummary.metric_date <= end_date
        ).all()

        # Aggregate metrics
        total_views = sum(s.total_item_investigations for s in summaries)
        unique_views = sum(s.unique_item_investigations for s in summaries)
        total_downloads = sum(s.total_item_requests for s in summaries)
        unique_downloads = sum(s.unique_item_requests for s in summaries)

        # Aggregate by type
        abstract_views = sum(s.abstract_views for s in summaries)
        full_text_views = sum(s.full_text_views for s in summaries)
        pdf_downloads = sum(s.pdf_downloads for s in summaries)
        xml_downloads = sum(s.xml_downloads for s in summaries)

        # Aggregate countries
        all_countries = {}
        for summary in summaries:
            if summary.top_countries:
                countries = json.loads(summary.top_countries)
                for country, count in countries.items():
                    all_countries[country] = all_countries.get(country, 0) + count

        # Sort countries by count
        top_countries = dict(sorted(all_countries.items(), key=lambda x: x[1], reverse=True)[:10])

        # Calculate trend
        trend = self._calculate_trend(summaries)

        return ArticleMetrics(
            manuscript_id=manuscript_id,
            title=manuscript.title if manuscript else "Unknown",
            total_views=total_views,
            unique_views=unique_views,
            total_downloads=total_downloads,
            unique_downloads=unique_downloads,
            abstract_views=abstract_views,
            full_text_views=full_text_views,
            pdf_downloads=pdf_downloads,
            xml_downloads=xml_downloads,
            top_countries=top_countries,
            trend=trend
        )

    def _calculate_trend(self, summaries: List[ArticleMetricSummary]) -> str:
        """Calculate trend (increasing/stable/decreasing)."""
        if len(summaries) < 7:
            return "insufficient_data"

        # Sort by date
        summaries_sorted = sorted(summaries, key=lambda s: s.metric_date)

        # Split into two halves
        mid = len(summaries_sorted) // 2
        first_half = summaries_sorted[:mid]
        second_half = summaries_sorted[mid:]

        # Compare averages
        avg_first = sum(s.total_item_investigations for s in first_half) / len(first_half)
        avg_second = sum(s.total_item_investigations for s in second_half) / len(second_half)

        if avg_second > avg_first * 1.2:
            return "increasing"
        elif avg_second < avg_first * 0.8:
            return "decreasing"
        else:
            return "stable"

    async def generate_insights(
        self,
        manuscript_id: int,
        db: Session
    ) -> ArticleInsights:
        """Generate AI-powered insights about article performance."""
        # Get metrics for last 30 days
        metrics = await self.get_article_metrics(manuscript_id, db=db)

        # Prepare context for LLM
        context = f"""Article Performance Metrics:

Title: {metrics.title}
Total Views: {metrics.total_views}
Unique Views: {metrics.unique_views}
Total Downloads: {metrics.total_downloads}
Unique Downloads: {metrics.unique_downloads}

Breakdown:
- Abstract views: {metrics.abstract_views}
- Full text views: {metrics.full_text_views}
- PDF downloads: {metrics.pdf_downloads}
- XML downloads: {metrics.xml_downloads}

Top Countries: {', '.join(f'{c} ({n})' for c, n in list(metrics.top_countries.items())[:5])}

Trend: {metrics.trend}
"""

        prompt = f"""{context}

Analyze these article metrics and provide insights.

Provide:
1. Performance Summary (1 sentence)
2. Interesting Patterns (2-3 observations)
3. Recommendations to Increase Visibility (2-3 actionable suggestions)

Respond in JSON format:
{{
    "performance_summary": "...",
    "interesting_patterns": ["...", "...", "..."],
    "recommendations": ["...", "...", "..."]
}}"""

        try:
            response = await self.llm.generate(
                prompt=prompt,
                format="json",
                temperature=0.5,
                max_tokens=300
            )

            insights_data = json.loads(response.text)

            return ArticleInsights(
                manuscript_id=manuscript_id,
                performance_summary=insights_data.get('performance_summary', ''),
                interesting_patterns=insights_data.get('interesting_patterns', []),
                recommendations=insights_data.get('recommendations', []),
                generated_at=datetime.utcnow()
            )

        except Exception as e:
            # Fallback insights
            return ArticleInsights(
                manuscript_id=manuscript_id,
                performance_summary=f"Article has {metrics.total_views} total views and {metrics.total_downloads} downloads in the last 30 days.",
                interesting_patterns=[
                    f"Performance trend is {metrics.trend}",
                    f"Top geographic interest from {list(metrics.top_countries.keys())[0] if metrics.top_countries else 'unknown'}"
                ],
                recommendations=[
                    "Share article on social media platforms",
                    "Submit to relevant research databases",
                    "Engage with authors to promote their work"
                ],
                generated_at=datetime.utcnow()
            )


# Singleton instance
_counter_service: Optional[COUNTERService] = None


def get_counter_service() -> COUNTERService:
    """Get singleton COUNTER service instance."""
    global _counter_service
    if _counter_service is None:
        _counter_service = COUNTERService()
    return _counter_service
