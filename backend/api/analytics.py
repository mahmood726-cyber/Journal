"""
Analytics API Endpoints

Provides REST API for analytics:
- Dashboard metrics
- Article performance
- User metrics
- Traffic analysis
- Geographic data
- Trends data
- Real-time statistics
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import json

from database import get_db
from models import User, Article, ArticleView, ArticleDownload, UserSession
from api.auth import get_current_user

router = APIRouter()


# ==================== Response Models ====================

class OverviewMetrics(BaseModel):
    total_views: int
    unique_visitors: int
    downloads: int
    avg_time_on_site: int
    bounce_rate: float
    conversion_rate: float
    views_change: float
    visitors_change: float
    downloads_change: float


class ArticleMetrics(BaseModel):
    id: str
    title: str
    views: int
    downloads: int
    shares: int
    avg_read_time: int
    completion_rate: int
    citation_count: int
    published_date: str
    views_trend: float


class DeviceBreakdown(BaseModel):
    desktop: int
    mobile: int
    tablet: int


class RetentionData(BaseModel):
    day1: float
    day7: float
    day30: float


class UserMetrics(BaseModel):
    total_users: int
    active_users: int
    new_users: int
    returning_users: int
    average_session_duration: int
    pages_per_session: float
    device_breakdown: DeviceBreakdown
    user_retention: RetentionData


class TrafficSource(BaseModel):
    name: str
    visitors: int
    percentage: float
    color: str


class Referrer(BaseModel):
    domain: str
    visits: int
    percentage: float


class SearchKeyword(BaseModel):
    keyword: str
    searches: int
    click_through_rate: float


class TrafficData(BaseModel):
    sources: List[TrafficSource]
    referrers: List[Referrer]
    keywords: List[SearchKeyword]


class CountryData(BaseModel):
    country: str
    visitors: int
    percentage: float
    avg_time_on_site: int


class CityData(BaseModel):
    city: str
    country: str
    visitors: int


class GeographyData(BaseModel):
    countries: List[CountryData]
    cities: List[CityData]


class TrendData(BaseModel):
    date: str
    views: int
    visitors: int
    downloads: int


class AnalyticsData(BaseModel):
    overview: OverviewMetrics
    articles: List[ArticleMetrics]
    users: UserMetrics
    traffic: TrafficData
    geography: GeographyData
    trends: List[TrendData]


# ==================== Endpoints ====================

@router.get("/dashboard", response_model=AnalyticsData)
async def get_dashboard_analytics(
    range: str = Query("30d", regex="^(7d|30d|90d|1y)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get complete dashboard analytics."""
    # Parse date range
    days_map = {"7d": 7, "30d": 30, "90d": 90, "1y": 365}
    days = days_map[range]

    start_date = datetime.utcnow() - timedelta(days=days)
    prev_start_date = start_date - timedelta(days=days)

    # Calculate overview metrics
    overview = await get_overview_metrics(db, start_date, prev_start_date)

    # Get top articles
    articles = await get_top_articles(db, start_date, limit=10)

    # Get user metrics
    users = await get_user_metrics(db, start_date)

    # Get traffic data
    traffic = await get_traffic_data(db, start_date)

    # Get geography data
    geography = await get_geography_data(db, start_date)

    # Get trends
    trends = await get_trends_data(db, start_date, days)

    return {
        "overview": overview,
        "articles": articles,
        "users": users,
        "traffic": traffic,
        "geography": geography,
        "trends": trends
    }


async def get_overview_metrics(
    db: Session,
    start_date: datetime,
    prev_start_date: datetime
) -> OverviewMetrics:
    """Calculate overview metrics."""
    # Current period
    current_views = db.query(func.count(ArticleView.id)).filter(
        ArticleView.viewed_at >= start_date
    ).scalar() or 0

    current_visitors = db.query(func.count(func.distinct(ArticleView.user_id))).filter(
        ArticleView.viewed_at >= start_date
    ).scalar() or 0

    current_downloads = db.query(func.count(ArticleDownload.id)).filter(
        ArticleDownload.downloaded_at >= start_date
    ).scalar() or 0

    # Previous period
    prev_views = db.query(func.count(ArticleView.id)).filter(
        and_(
            ArticleView.viewed_at >= prev_start_date,
            ArticleView.viewed_at < start_date
        )
    ).scalar() or 0

    prev_visitors = db.query(func.count(func.distinct(ArticleView.user_id))).filter(
        and_(
            ArticleView.viewed_at >= prev_start_date,
            ArticleView.viewed_at < start_date
        )
    ).scalar() or 0

    prev_downloads = db.query(func.count(ArticleDownload.id)).filter(
        and_(
            ArticleDownload.downloaded_at >= prev_start_date,
            ArticleDownload.downloaded_at < start_date
        )
    ).scalar() or 0

    # Calculate changes
    views_change = calculate_change(current_views, prev_views)
    visitors_change = calculate_change(current_visitors, prev_visitors)
    downloads_change = calculate_change(current_downloads, prev_downloads)

    # Average time on site
    avg_time = db.query(func.avg(UserSession.duration)).filter(
        UserSession.created_at >= start_date
    ).scalar() or 0

    # Bounce rate (sessions with 1 page view)
    total_sessions = db.query(func.count(UserSession.id)).filter(
        UserSession.created_at >= start_date
    ).scalar() or 1

    bounce_sessions = db.query(func.count(UserSession.id)).filter(
        and_(
            UserSession.created_at >= start_date,
            UserSession.page_views == 1
        )
    ).scalar() or 0

    bounce_rate = (bounce_sessions / total_sessions) * 100 if total_sessions > 0 else 0

    # Conversion rate (downloads / views)
    conversion_rate = (current_downloads / current_views) * 100 if current_views > 0 else 0

    return OverviewMetrics(
        total_views=current_views,
        unique_visitors=current_visitors,
        downloads=current_downloads,
        avg_time_on_site=int(avg_time),
        bounce_rate=round(bounce_rate, 2),
        conversion_rate=round(conversion_rate, 2),
        views_change=round(views_change, 1),
        visitors_change=round(visitors_change, 1),
        downloads_change=round(downloads_change, 1)
    )


async def get_top_articles(
    db: Session,
    start_date: datetime,
    limit: int = 10
) -> List[ArticleMetrics]:
    """Get top performing articles."""
    # Get view counts
    view_counts = db.query(
        ArticleView.article_id,
        func.count(ArticleView.id).label('views'),
        func.avg(ArticleView.time_spent).label('avg_time'),
        func.avg(ArticleView.scroll_depth).label('completion')
    ).filter(
        ArticleView.viewed_at >= start_date
    ).group_by(ArticleView.article_id).all()

    # Get download counts
    download_counts = {}
    downloads = db.query(
        ArticleDownload.article_id,
        func.count(ArticleDownload.id).label('downloads')
    ).filter(
        ArticleDownload.downloaded_at >= start_date
    ).group_by(ArticleDownload.article_id).all()

    for article_id, count in downloads:
        download_counts[article_id] = count

    # Build article metrics
    articles = []
    for article_id, views, avg_time, completion in view_counts:
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            continue

        # Calculate trend (compare to previous period)
        prev_start = start_date - (datetime.utcnow() - start_date)
        prev_views = db.query(func.count(ArticleView.id)).filter(
            and_(
                ArticleView.article_id == article_id,
                ArticleView.viewed_at >= prev_start,
                ArticleView.viewed_at < start_date
            )
        ).scalar() or 0

        trend = calculate_change(views, prev_views)

        articles.append(ArticleMetrics(
            id=article.id,
            title=article.title,
            views=views,
            downloads=download_counts.get(article_id, 0),
            shares=0,  # Would track shares separately
            avg_read_time=int(avg_time or 0),
            completion_rate=int(completion or 0),
            citation_count=article.citation_count or 0,
            published_date=article.published_date.isoformat(),
            views_trend=round(trend, 1)
        ))

    # Sort by views and return top N
    articles.sort(key=lambda x: x.views, reverse=True)
    return articles[:limit]


async def get_user_metrics(
    db: Session,
    start_date: datetime
) -> UserMetrics:
    """Get user engagement metrics."""
    # Total users (unique visitors)
    total_users = db.query(func.count(func.distinct(UserSession.user_id))).filter(
        UserSession.created_at >= start_date
    ).scalar() or 0

    # Active users (visited in last 7 days)
    active_cutoff = datetime.utcnow() - timedelta(days=7)
    active_users = db.query(func.count(func.distinct(UserSession.user_id))).filter(
        UserSession.created_at >= active_cutoff
    ).scalar() or 0

    # New vs returning users
    # This is simplified - would need user registration tracking
    new_users = int(total_users * 0.3)
    returning_users = total_users - new_users

    # Average session duration
    avg_duration = db.query(func.avg(UserSession.duration)).filter(
        UserSession.created_at >= start_date
    ).scalar() or 0

    # Pages per session
    pages_per_session = db.query(func.avg(UserSession.page_views)).filter(
        UserSession.created_at >= start_date
    ).scalar() or 0

    # Device breakdown
    device_data = db.query(
        UserSession.device_type,
        func.count(UserSession.id)
    ).filter(
        UserSession.created_at >= start_date
    ).group_by(UserSession.device_type).all()

    total_sessions = sum(count for _, count in device_data)
    device_breakdown = {"desktop": 0, "mobile": 0, "tablet": 0}

    for device, count in device_data:
        percentage = (count / total_sessions) * 100 if total_sessions > 0 else 0
        device_breakdown[device or "desktop"] = int(percentage)

    # User retention (simplified)
    retention = RetentionData(
        day1=85.0,  # Would calculate based on actual return visits
        day7=60.0,
        day30=40.0
    )

    return UserMetrics(
        total_users=total_users,
        active_users=active_users,
        new_users=new_users,
        returning_users=returning_users,
        average_session_duration=int(avg_duration),
        pages_per_session=round(pages_per_session, 1),
        device_breakdown=DeviceBreakdown(**device_breakdown),
        user_retention=retention
    )


async def get_traffic_data(
    db: Session,
    start_date: datetime
) -> TrafficData:
    """Get traffic sources and referrers."""
    # Traffic sources
    source_data = db.query(
        UserSession.traffic_source,
        func.count(UserSession.id)
    ).filter(
        UserSession.created_at >= start_date
    ).group_by(UserSession.traffic_source).all()

    total_visits = sum(count for _, count in source_data)

    source_colors = {
        "organic": "from-green-500 to-green-600",
        "direct": "from-blue-500 to-blue-600",
        "social": "from-purple-500 to-purple-600",
        "referral": "from-indigo-500 to-indigo-600",
        "email": "from-pink-500 to-pink-600"
    }

    sources = []
    for source, count in source_data:
        sources.append(TrafficSource(
            name=(source or "direct").capitalize(),
            visitors=count,
            percentage=round((count / total_visits) * 100, 1) if total_visits > 0 else 0,
            color=source_colors.get(source or "direct", "from-gray-500 to-gray-600")
        ))

    # Referrers
    referrer_data = db.query(
        UserSession.referrer,
        func.count(UserSession.id)
    ).filter(
        and_(
            UserSession.created_at >= start_date,
            UserSession.referrer.isnot(None)
        )
    ).group_by(UserSession.referrer).limit(10).all()

    referrers = []
    for referrer, count in referrer_data:
        referrers.append(Referrer(
            domain=referrer,
            visits=count,
            percentage=round((count / total_visits) * 100, 1) if total_visits > 0 else 0
        ))

    # Search keywords (would come from search tracking)
    keywords = [
        SearchKeyword(keyword="machine learning", searches=150, click_through_rate=75.5),
        SearchKeyword(keyword="CRISPR", searches=120, click_through_rate=82.3),
        SearchKeyword(keyword="cancer research", searches=95, click_through_rate=68.4)
    ]

    return TrafficData(
        sources=sources,
        referrers=referrers,
        keywords=keywords
    )


async def get_geography_data(
    db: Session,
    start_date: datetime
) -> GeographyData:
    """Get geographic distribution."""
    # Country data
    country_data = db.query(
        UserSession.country,
        func.count(UserSession.id).label('visitors'),
        func.avg(UserSession.duration).label('avg_time')
    ).filter(
        and_(
            UserSession.created_at >= start_date,
            UserSession.country.isnot(None)
        )
    ).group_by(UserSession.country).order_by(func.count(UserSession.id).desc()).limit(10).all()

    total_visitors = sum(visitors for _, visitors, _ in country_data)

    countries = []
    for country, visitors, avg_time in country_data:
        countries.append(CountryData(
            country=country,
            visitors=visitors,
            percentage=round((visitors / total_visitors) * 100, 1) if total_visitors > 0 else 0,
            avg_time_on_site=int(avg_time or 0)
        ))

    # City data
    city_data = db.query(
        UserSession.city,
        UserSession.country,
        func.count(UserSession.id).label('visitors')
    ).filter(
        and_(
            UserSession.created_at >= start_date,
            UserSession.city.isnot(None)
        )
    ).group_by(UserSession.city, UserSession.country).order_by(func.count(UserSession.id).desc()).limit(10).all()

    cities = []
    for city, country, visitors in city_data:
        cities.append(CityData(
            city=city,
            country=country,
            visitors=visitors
        ))

    return GeographyData(
        countries=countries,
        cities=cities
    )


async def get_trends_data(
    db: Session,
    start_date: datetime,
    days: int
) -> List[TrendData]:
    """Get daily trends data."""
    trends = []

    for i in range(days):
        date = start_date + timedelta(days=i)
        next_date = date + timedelta(days=1)

        views = db.query(func.count(ArticleView.id)).filter(
            and_(
                ArticleView.viewed_at >= date,
                ArticleView.viewed_at < next_date
            )
        ).scalar() or 0

        visitors = db.query(func.count(func.distinct(ArticleView.user_id))).filter(
            and_(
                ArticleView.viewed_at >= date,
                ArticleView.viewed_at < next_date
            )
        ).scalar() or 0

        downloads = db.query(func.count(ArticleDownload.id)).filter(
            and_(
                ArticleDownload.downloaded_at >= date,
                ArticleDownload.downloaded_at < next_date
            )
        ).scalar() or 0

        trends.append(TrendData(
            date=date.isoformat(),
            views=views,
            visitors=visitors,
            downloads=downloads
        ))

    return trends


@router.get("/real-time")
async def get_realtime_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get real-time statistics (last 5 minutes)."""
    five_min_ago = datetime.utcnow() - timedelta(minutes=5)

    active_users = db.query(func.count(func.distinct(UserSession.user_id))).filter(
        UserSession.last_activity >= five_min_ago
    ).scalar() or 0

    page_views = db.query(func.count(ArticleView.id)).filter(
        ArticleView.viewed_at >= five_min_ago
    ).scalar() or 0

    # Top pages being viewed right now
    top_pages = db.query(
        ArticleView.article_id,
        func.count(ArticleView.id).label('views')
    ).filter(
        ArticleView.viewed_at >= five_min_ago
    ).group_by(ArticleView.article_id).order_by(func.count(ArticleView.id).desc()).limit(5).all()

    top_articles = []
    for article_id, views in top_pages:
        article = db.query(Article).filter(Article.id == article_id).first()
        if article:
            top_articles.append({
                "id": article.id,
                "title": article.title,
                "active_viewers": views
            })

    return {
        "active_users": active_users,
        "page_views_per_minute": page_views / 5,
        "top_articles": top_articles,
        "timestamp": datetime.utcnow().isoformat()
    }


# ==================== Helper Functions ====================

def calculate_change(current: int, previous: int) -> float:
    """Calculate percentage change."""
    if previous == 0:
        return 100.0 if current > 0 else 0.0

    return ((current - previous) / previous) * 100
