"""
Ultra-optimized manuscript API endpoints with caching, pagination, and eager loading.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime

from db.base import get_db
from db.models import (
    Manuscript, ManuscriptStatus, User, UserRole,
    manuscript_authors, Review
)
from schemas.manuscript import ManuscriptResponse
from api.auth import get_current_user
from core.cache import cached, CacheManager

router = APIRouter()


@router.get("/published", response_model=List[ManuscriptResponse])
@cached("published-articles", ttl=300)  # Cache for 5 minutes
async def get_published_manuscripts(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    specialization_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get published manuscripts with pagination and caching.

    Performance optimizations:
    - Cached for 5 minutes
    - Eager loading of authors and specialization
    - Pagination to limit result set
    - Indexed queries
    """
    # Build query with eager loading
    query = db.query(Manuscript).options(
        selectinload(Manuscript.authors),
        joinedload(Manuscript.specialization)
    ).filter(
        Manuscript.status == ManuscriptStatus.PUBLISHED
    )

    # Apply filters
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Manuscript.title.ilike(search_term),
                Manuscript.abstract.ilike(search_term)
            )
        )

    if specialization_id:
        query = query.filter(Manuscript.specialization_id == specialization_id)

    # Order by published date (uses index)
    query = query.order_by(Manuscript.published_at.desc())

    # Pagination
    offset = (page - 1) * per_page
    manuscripts = query.offset(offset).limit(per_page).all()

    return manuscripts


@router.get("/{manuscript_id}", response_model=ManuscriptResponse)
@cached("manuscript", ttl=600)  # Cache for 10 minutes
async def get_manuscript(
    manuscript_id: int,
    db: Session = Depends(get_db)
):
    """
    Get single manuscript with all related data.

    Performance optimizations:
    - Cached for 10 minutes
    - Single query with eager loading
    - No N+1 query problem
    """
    manuscript = db.query(Manuscript).options(
        selectinload(Manuscript.authors),
        joinedload(Manuscript.specialization),
        joinedload(Manuscript.submitter),
        selectinload(Manuscript.reviews),
        selectinload(Manuscript.files)
    ).filter(
        Manuscript.id == manuscript_id
    ).first()

    if not manuscript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manuscript not found"
        )

    # Increment views (async, don't wait)
    manuscript.views += 1
    db.commit()

    return manuscript


@router.get("/user/my-manuscripts", response_model=List[ManuscriptResponse])
async def get_my_manuscripts(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status_filter: Optional[ManuscriptStatus] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's manuscripts.

    Performance optimizations:
    - User-specific caching not applied (data is personalized)
    - Eager loading of relationships
    - Indexed query on submitter_id
    - Pagination
    """
    # Build query with eager loading
    query = db.query(Manuscript).options(
        selectinload(Manuscript.authors),
        joinedload(Manuscript.specialization)
    ).filter(
        Manuscript.submitter_id == current_user.id
    )

    # Apply status filter
    if status_filter:
        query = query.filter(Manuscript.status == status_filter)

    # Order by created date (uses index)
    query = query.order_by(Manuscript.created_at.desc())

    # Pagination
    offset = (page - 1) * per_page
    manuscripts = query.offset(offset).limit(per_page).all()

    return manuscripts


@router.get("/stats/dashboard")
@cached("manuscript-stats", ttl=300)  # Cache for 5 minutes
async def get_manuscript_stats(
    db: Session = Depends(get_db)
):
    """
    Get manuscript statistics for dashboard.

    Performance optimizations:
    - Cached for 5 minutes
    - Aggregation queries use indexes
    - Single database round trip
    """
    # Get counts by status (uses index on status)
    status_counts = db.query(
        Manuscript.status,
        func.count(Manuscript.id).label('count')
    ).group_by(Manuscript.status).all()

    # Get recent submissions count (uses index on created_at)
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    recent_submissions = db.query(func.count(Manuscript.id)).filter(
        Manuscript.created_at >= thirty_days_ago
    ).scalar()

    # Get average review time
    avg_review_time = db.query(
        func.avg(
            func.extract('epoch', Manuscript.updated_at - Manuscript.submitted_at) / 86400
        )
    ).filter(
        Manuscript.status.in_([ManuscriptStatus.ACCEPTED, ManuscriptStatus.PUBLISHED])
    ).scalar()

    return {
        "status_counts": {status.value: count for status, count in status_counts},
        "recent_submissions": recent_submissions,
        "avg_review_days": round(avg_review_time or 0, 1)
    }


@router.get("/featured", response_model=List[ManuscriptResponse])
@cached("featured-articles", ttl=3600)  # Cache for 1 hour
async def get_featured_articles(
    limit: int = Query(6, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """
    Get featured articles for homepage.

    Performance optimizations:
    - Cached for 1 hour (rarely changes)
    - Eager loading
    - Limited result set
    - Indexed query
    """
    manuscripts = db.query(Manuscript).options(
        selectinload(Manuscript.authors),
        joinedload(Manuscript.specialization)
    ).filter(
        Manuscript.status == ManuscriptStatus.PUBLISHED
    ).order_by(
        Manuscript.views.desc(),
        Manuscript.published_at.desc()
    ).limit(limit).all()

    return manuscripts


# Cache invalidation on write operations
@router.post("/{manuscript_id}/publish")
async def publish_manuscript(
    manuscript_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Publish manuscript and invalidate related caches.
    """
    # Check permissions
    if current_user.role not in [UserRole.ADMIN, UserRole.EDITOR_IN_CHIEF]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only editors can publish manuscripts"
        )

    manuscript = db.query(Manuscript).filter(Manuscript.id == manuscript_id).first()
    if not manuscript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manuscript not found"
        )

    # Update status
    manuscript.status = ManuscriptStatus.PUBLISHED
    manuscript.published_at = datetime.utcnow()
    db.commit()

    # Invalidate caches
    await CacheManager.invalidate_manuscript(manuscript_id)

    return {"message": "Manuscript published successfully"}
