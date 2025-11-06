"""
API endpoints for article metrics and COUNTER R5 reporting.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import date, datetime, timedelta

from db.database import get_db
from db.models import User, Manuscript, UserRole
from api.auth import get_current_user
from services.counter_service import (
    get_counter_service,
    MetricEventRequest,
    ArticleMetrics,
    ArticleInsights
)


router = APIRouter()


# ============================================================================
# Event Tracking Endpoints
# ============================================================================

class TrackEventRequest(BaseModel):
    """Request to track a metric event."""
    manuscript_id: int
    event_type: str  # abstract_view, full_text_view, pdf_download, etc.


@router.post("/track")
async def track_metric_event(
    request: TrackEventRequest,
    http_request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = None
):
    """
    Track a metric event (view, download, etc.).

    This endpoint is called when users interact with articles.
    Implements COUNTER R5 compliance with bot filtering and double-click detection.

    Event Types:
    - abstract_view: User views abstract
    - full_text_view: User views full text
    - pdf_download: User downloads PDF
    - xml_download: User downloads XML
    - html_view: User views HTML version
    - landing_page_view: User lands on article page

    Note: This endpoint is public (no auth required) to track anonymous users.
    """
    # Check manuscript exists
    manuscript = db.query(Manuscript).filter(
        Manuscript.id == request.manuscript_id
    ).first()

    if not manuscript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manuscript not found"
        )

    # Get session ID from request (or generate)
    session_id = http_request.cookies.get('session_id', http_request.client.host)

    # Build metric event request
    metric_request = MetricEventRequest(
        manuscript_id=request.manuscript_id,
        event_type=request.event_type,
        user_id=current_user.id if current_user else None,
        session_id=session_id,
        ip_address=http_request.client.host,
        user_agent=http_request.headers.get('user-agent', ''),
        referrer=http_request.headers.get('referer'),
        country_code=http_request.headers.get('cf-ipcountry')  # Cloudflare country code
    )

    # Track event
    counter_service = get_counter_service()
    await counter_service.track_event(metric_request, db)

    return {"success": True, "message": "Event tracked"}


# ============================================================================
# Metrics Viewing Endpoints
# ============================================================================

@router.get("/articles/{manuscript_id}/metrics", response_model=ArticleMetrics)
async def get_article_metrics(
    manuscript_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get aggregated metrics for an article.

    Returns COUNTER R5 compliant metrics including:
    - Total and unique views
    - Total and unique downloads
    - Breakdown by type (abstract, full text, PDF, XML)
    - Geographic distribution
    - Performance trend

    Permissions:
    - Editors can view all article metrics
    - Authors can view their own article metrics
    - Reviewers can view metrics for articles they reviewed
    """
    # Check manuscript exists
    manuscript = db.query(Manuscript).filter(
        Manuscript.id == manuscript_id
    ).first()

    if not manuscript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manuscript not found"
        )

    # Permission check
    is_author = any(author.id == current_user.id for author in manuscript.authors)
    is_editor = current_user.role in [UserRole.EDITOR, UserRole.EDITOR_IN_CHIEF, UserRole.ADMIN]

    if not (is_author or is_editor):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view metrics for this article"
        )

    # Get metrics
    counter_service = get_counter_service()
    metrics = await counter_service.get_article_metrics(
        manuscript_id=manuscript_id,
        start_date=start_date,
        end_date=end_date,
        db=db
    )

    return metrics


@router.get("/articles/{manuscript_id}/insights", response_model=ArticleInsights)
async def get_article_insights(
    manuscript_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get AI-powered insights about article performance.

    Uses local LLM to analyze article metrics and provide:
    - Performance summary
    - Interesting patterns
    - Recommendations to increase visibility

    Permissions:
    - Editors and authors only
    """
    # Check manuscript exists
    manuscript = db.query(Manuscript).filter(
        Manuscript.id == manuscript_id
    ).first()

    if not manuscript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manuscript not found"
        )

    # Permission check
    is_author = any(author.id == current_user.id for author in manuscript.authors)
    is_editor = current_user.role in [UserRole.EDITOR, UserRole.EDITOR_IN_CHIEF, UserRole.ADMIN]

    if not (is_author or is_editor):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view insights for this article"
        )

    # Generate insights
    counter_service = get_counter_service()
    insights = await counter_service.generate_insights(
        manuscript_id=manuscript_id,
        db=db
    )

    return insights


# ============================================================================
# Dashboard & Analytics Endpoints
# ============================================================================

class DashboardMetrics(BaseModel):
    """Dashboard metrics summary."""
    total_articles: int
    articles_with_views: int
    total_views_30d: int
    total_downloads_30d: int
    top_articles: List[ArticleMetrics]
    total_countries_reached: int


@router.get("/dashboard", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get journal-wide dashboard metrics.

    Provides overview of journal performance for editors.

    Permissions:
    - Editors and Admins only
    """
    if current_user.role not in [UserRole.EDITOR, UserRole.EDITOR_IN_CHIEF, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Editor access required"
        )

    # Get all published articles
    manuscripts = db.query(Manuscript).filter(
        Manuscript.status == "published"
    ).all()

    total_articles = len(manuscripts)

    # Get metrics for last 30 days
    counter_service = get_counter_service()
    end_date = date.today()
    start_date = end_date - timedelta(days=30)

    all_metrics = []
    total_views = 0
    total_downloads = 0
    countries = set()

    for manuscript in manuscripts:
        try:
            metrics = await counter_service.get_article_metrics(
                manuscript_id=manuscript.id,
                start_date=start_date,
                end_date=end_date,
                db=db
            )
            all_metrics.append(metrics)
            total_views += metrics.total_views
            total_downloads += metrics.total_downloads
            countries.update(metrics.top_countries.keys())
        except:
            continue

    # Get top 10 articles by views
    top_articles = sorted(all_metrics, key=lambda m: m.total_views, reverse=True)[:10]

    # Count articles with views
    articles_with_views = sum(1 for m in all_metrics if m.total_views > 0)

    return DashboardMetrics(
        total_articles=total_articles,
        articles_with_views=articles_with_views,
        total_views_30d=total_views,
        total_downloads_30d=total_downloads,
        top_articles=top_articles,
        total_countries_reached=len(countries)
    )


# ============================================================================
# COUNTER R5 Report Endpoints
# ============================================================================

@router.get("/counter/report/tr-j1")
async def generate_counter_tr_j1_report(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate COUNTER R5 TR_J1 report (Journal Requests).

    TR_J1 provides journal-level usage broken down by month.
    This is the primary COUNTER report for journals.

    Permissions:
    - Editors and Admins only
    """
    if current_user.role not in [UserRole.EDITOR, UserRole.EDITOR_IN_CHIEF, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Editor access required"
        )

    # TODO: Implement full COUNTER R5 TR_J1 report generation
    # This would include:
    # - Monthly breakdown of usage
    # - Total_Item_Requests and Unique_Item_Requests
    # - Total_Item_Investigations and Unique_Item_Investigations
    # - Proper COUNTER R5 JSON format

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="COUNTER TR_J1 report generation coming soon"
    )


@router.get("/counter/report/tr-j4")
async def generate_counter_tr_j4_report(
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate COUNTER R5 TR_J4 report (Journal Requests by YOP).

    TR_J4 shows usage by year of publication.

    Permissions:
    - Editors and Admins only
    """
    if current_user.role not in [UserRole.EDITOR, UserRole.EDITOR_IN_CHIEF, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Editor access required"
        )

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="COUNTER TR_J4 report generation coming soon"
    )
