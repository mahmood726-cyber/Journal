"""
Issue Management API endpoints.

Handles:
- Creating and managing journal issues
- Assigning manuscripts to issues
- Table of contents management
- Issue publication
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional
from datetime import datetime
import os
import shutil

from db.base import get_db
from db.models import (
    User,
    Manuscript,
    ManuscriptStatus,
    UserRole,
    Issue,
    manuscript_authors
)
from schemas.issues import (
    IssueCreate,
    IssueResponse,
    IssueUpdate,
    IssueList,
    ArticleInIssue,
    IssueTableOfContents,
    AddArticleToIssue,
    ReorderArticles,
    IssuePublishRequest,
    IssueStatistics
)
from api.auth import get_current_user
from api.users import require_role
from services.email_service import email_service
from core.config import settings

router = APIRouter()


def generate_issue_doi(volume: int, number: int, year: int) -> Optional[str]:
    """Generate DOI for an issue."""
    if not settings.DOI_PREFIX:
        return None

    return f"{settings.DOI_PREFIX}/issue.{year}.v{volume}.n{number}"


def generate_article_doi(manuscript_id: str, year: int) -> Optional[str]:
    """Generate DOI for an article."""
    if not settings.DOI_PREFIX:
        return None

    return f"{settings.DOI_PREFIX}/{manuscript_id}.{year}"


@router.get("/", response_model=IssueList)
async def list_issues(
    year: Optional[int] = None,
    volume: Optional[int] = None,
    published_only: bool = False,
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all issues with filtering and pagination.

    Public users see only published issues.
    Editors see all issues.
    """
    query = db.query(Issue)

    # Access control
    if current_user.role not in [UserRole.EDITOR_IN_CHIEF, UserRole.ASSOCIATE_EDITOR, UserRole.ADMIN]:
        query = query.filter(Issue.is_published == True)
    elif published_only:
        query = query.filter(Issue.is_published == True)

    # Apply filters
    if year:
        query = query.filter(Issue.year == year)
    if volume:
        query = query.filter(Issue.volume == volume)

    # Count total
    total = query.count()

    # Pagination and ordering
    offset = (page - 1) * page_size
    issues = query.order_by(
        Issue.year.desc(),
        Issue.volume.desc(),
        Issue.number.desc()
    ).offset(offset).limit(page_size).all()

    # Enrich with article count
    response_issues = []
    for issue in issues:
        article_count = db.query(Manuscript).filter(
            and_(
                Manuscript.volume == issue.volume,
                Manuscript.issue == issue.number,
                Manuscript.status == ManuscriptStatus.PUBLISHED
            )
        ).count()

        issue_dict = IssueResponse.from_orm(issue).dict()
        issue_dict['article_count'] = article_count

        response_issues.append(IssueResponse(**issue_dict))

    return IssueList(
        total=total,
        issues=response_issues,
        page=page,
        page_size=page_size
    )


@router.post("/", response_model=IssueResponse, status_code=status.HTTP_201_CREATED)
@require_role([UserRole.EDITOR_IN_CHIEF, UserRole.ASSOCIATE_EDITOR])
async def create_issue(
    issue_data: IssueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new issue.

    Validates that volume/number/year combination is unique.
    """
    # Check if issue already exists
    existing = db.query(Issue).filter(
        and_(
            Issue.volume == issue_data.volume,
            Issue.number == issue_data.number,
            Issue.year == issue_data.year
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Issue Vol {issue_data.volume} No {issue_data.number} ({issue_data.year}) already exists"
        )

    # Generate DOI if configured
    doi = generate_issue_doi(issue_data.volume, issue_data.number, issue_data.year)

    # Create issue
    new_issue = Issue(
        volume=issue_data.volume,
        number=issue_data.number,
        year=issue_data.year,
        title=issue_data.title,
        description=issue_data.description,
        cover_image_url=issue_data.cover_image_url,
        scheduled_publication=issue_data.scheduled_publication,
        doi=doi,
        is_published=False
    )

    db.add(new_issue)
    db.commit()
    db.refresh(new_issue)

    return new_issue


@router.get("/{issue_id}", response_model=IssueResponse)
async def get_issue(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get details of a specific issue."""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()

    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )

    # Access control
    if not issue.is_published and current_user.role not in [
        UserRole.EDITOR_IN_CHIEF,
        UserRole.ASSOCIATE_EDITOR,
        UserRole.ADMIN
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view unpublished issues"
        )

    # Enrich with article count
    article_count = db.query(Manuscript).filter(
        and_(
            Manuscript.volume == issue.volume,
            Manuscript.issue == issue.number,
            Manuscript.status == ManuscriptStatus.PUBLISHED
        )
    ).count()

    issue_dict = IssueResponse.from_orm(issue).dict()
    issue_dict['article_count'] = article_count

    return IssueResponse(**issue_dict)


@router.patch("/{issue_id}", response_model=IssueResponse)
@require_role([UserRole.EDITOR_IN_CHIEF, UserRole.ASSOCIATE_EDITOR])
async def update_issue(
    issue_id: int,
    update_data: IssueUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update issue details."""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()

    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )

    if issue.is_published:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update published issue. Create a new issue instead."
        )

    # Update fields
    if update_data.title is not None:
        issue.title = update_data.title
    if update_data.description is not None:
        issue.description = update_data.description
    if update_data.cover_image_url is not None:
        issue.cover_image_url = update_data.cover_image_url
    if update_data.scheduled_publication is not None:
        issue.scheduled_publication = update_data.scheduled_publication

    db.commit()
    db.refresh(issue)

    return issue


@router.post("/{issue_id}/cover", response_model=IssueResponse)
@require_role([UserRole.EDITOR_IN_CHIEF, UserRole.ASSOCIATE_EDITOR])
async def upload_cover_image(
    issue_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload cover image for issue."""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()

    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )

    # Validate file type
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_ext} not allowed. Allowed: {', '.join(allowed_extensions)}"
        )

    # Save file
    upload_dir = f"{settings.UPLOAD_DIR}/issues/covers"
    os.makedirs(upload_dir, exist_ok=True)

    filename = f"vol{issue.volume}_no{issue.number}_{issue.year}{file_ext}"
    file_path = os.path.join(upload_dir, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Update issue
    issue.cover_image_url = f"/uploads/issues/covers/{filename}"

    db.commit()
    db.refresh(issue)

    return issue


@router.get("/{issue_id}/toc", response_model=IssueTableOfContents)
async def get_table_of_contents(
    issue_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get table of contents for an issue.

    Returns all manuscripts assigned to this issue in order.
    """
    issue = db.query(Issue).filter(Issue.id == issue_id).first()

    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )

    # Access control
    if not issue.is_published and current_user.role not in [
        UserRole.EDITOR_IN_CHIEF,
        UserRole.ASSOCIATE_EDITOR,
        UserRole.ADMIN
    ]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view unpublished issue contents"
        )

    # Get manuscripts
    manuscripts = db.query(Manuscript).filter(
        and_(
            Manuscript.volume == issue.volume,
            Manuscript.issue == issue.number
        )
    ).order_by(Manuscript.article_order).all()

    # Build article list
    articles = []
    for manuscript in manuscripts:
        # Get authors
        authors = db.query(User).join(
            manuscript_authors,
            User.id == manuscript_authors.c.author_id
        ).filter(
            manuscript_authors.c.manuscript_id == manuscript.id
        ).order_by(
            manuscript_authors.c.author_order
        ).all()

        author_names = [f"{a.first_name} {a.last_name}" for a in authors]

        articles.append(ArticleInIssue(
            id=manuscript.id,
            manuscript_id=manuscript.manuscript_id,
            title=manuscript.title,
            authors=author_names,
            page_start=manuscript.page_start,
            page_end=manuscript.page_end,
            doi=manuscript.doi,
            article_order=manuscript.article_order or 0,
            article_type=manuscript.article_type,
            published_at=manuscript.published_at or datetime.now()
        ))

    # Enrich issue
    issue_dict = IssueResponse.from_orm(issue).dict()
    issue_dict['article_count'] = len(articles)

    return IssueTableOfContents(
        issue=IssueResponse(**issue_dict),
        articles=articles
    )


@router.post("/{issue_id}/articles", response_model=IssueResponse)
@require_role([UserRole.EDITOR_IN_CHIEF, UserRole.ASSOCIATE_EDITOR])
async def add_article_to_issue(
    issue_id: int,
    article_data: AddArticleToIssue,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a manuscript to an issue.

    Manuscript must be in IN_PRODUCTION status.
    """
    issue = db.query(Issue).filter(Issue.id == issue_id).first()

    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )

    if issue.is_published:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add articles to published issue"
        )

    # Get manuscript
    manuscript = db.query(Manuscript).filter(Manuscript.id == article_data.manuscript_id).first()

    if not manuscript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manuscript not found"
        )

    if manuscript.status != ManuscriptStatus.IN_PRODUCTION:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Manuscript must be in IN_PRODUCTION status (current: {manuscript.status})"
        )

    # Check if already assigned to an issue
    if manuscript.volume is not None and manuscript.issue is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Manuscript already assigned to Vol {manuscript.volume} No {manuscript.issue}"
        )

    # Get next article order
    max_order = db.query(func.max(Manuscript.article_order)).filter(
        and_(
            Manuscript.volume == issue.volume,
            Manuscript.issue == issue.number
        )
    ).scalar() or 0

    # Assign to issue
    manuscript.volume = issue.volume
    manuscript.issue = issue.number
    manuscript.article_order = max_order + 1

    if article_data.page_start:
        manuscript.page_start = article_data.page_start
    if article_data.page_end:
        manuscript.page_end = article_data.page_end

    db.commit()
    db.refresh(issue)

    return issue


@router.delete("/{issue_id}/articles/{manuscript_id}", response_model=IssueResponse)
@require_role([UserRole.EDITOR_IN_CHIEF, UserRole.ASSOCIATE_EDITOR])
async def remove_article_from_issue(
    issue_id: int,
    manuscript_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a manuscript from an issue."""
    issue = db.query(Issue).filter(Issue.id == issue_id).first()

    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )

    if issue.is_published:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot remove articles from published issue"
        )

    manuscript = db.query(Manuscript).filter(Manuscript.id == manuscript_id).first()

    if not manuscript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manuscript not found"
        )

    # Remove from issue
    manuscript.volume = None
    manuscript.issue = None
    manuscript.article_order = None
    manuscript.page_start = None
    manuscript.page_end = None

    db.commit()
    db.refresh(issue)

    return issue


@router.post("/{issue_id}/reorder", response_model=IssueResponse)
@require_role([UserRole.EDITOR_IN_CHIEF, UserRole.ASSOCIATE_EDITOR])
async def reorder_articles(
    issue_id: int,
    reorder_data: ReorderArticles,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Reorder articles in an issue.

    Provide list of {manuscript_id, order} pairs.
    """
    issue = db.query(Issue).filter(Issue.id == issue_id).first()

    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )

    if issue.is_published:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot reorder articles in published issue"
        )

    # Update article orders
    for item in reorder_data.article_orders:
        manuscript = db.query(Manuscript).filter(Manuscript.id == item['manuscript_id']).first()

        if not manuscript:
            continue

        # Verify manuscript is in this issue
        if manuscript.volume != issue.volume or manuscript.issue != issue.number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Manuscript {manuscript.manuscript_id} is not in this issue"
            )

        manuscript.article_order = item['order']

    db.commit()
    db.refresh(issue)

    return issue


@router.post("/{issue_id}/publish", response_model=IssueResponse)
@require_role([UserRole.EDITOR_IN_CHIEF])
async def publish_issue(
    issue_id: int,
    publish_request: IssuePublishRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Publish an issue.

    - Marks issue as published
    - Optionally assigns DOIs to all articles
    - Publishes all manuscripts in issue
    - Sends notifications to authors
    """
    issue = db.query(Issue).filter(Issue.id == issue_id).first()

    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )

    if issue.is_published:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Issue is already published"
        )

    # Get all manuscripts in issue
    manuscripts = db.query(Manuscript).filter(
        and_(
            Manuscript.volume == issue.volume,
            Manuscript.issue == issue.number
        )
    ).all()

    if not manuscripts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot publish empty issue"
        )

    # Publish date
    publish_date = publish_request.publish_date or datetime.now()

    # Update issue
    issue.is_published = True
    issue.published_at = publish_date

    # Publish all manuscripts
    for manuscript in manuscripts:
        manuscript.status = ManuscriptStatus.PUBLISHED
        manuscript.published_at = publish_date

        # Assign DOI if requested and not already assigned
        if publish_request.assign_dois and not manuscript.doi:
            manuscript.doi = generate_article_doi(manuscript.manuscript_id, issue.year)

    db.commit()

    # Send notifications
    if publish_request.send_notifications:
        for manuscript in manuscripts:
            author = db.query(User).filter(User.id == manuscript.submitter_id).first()
            if author:
                try:
                    await email_service.send_email(
                        recipients=[author.email],
                        subject=f"Your Article Has Been Published: {manuscript.title}",
                        template_name="article_published",
                        context={
                            'author_name': f"{author.first_name} {author.last_name}",
                            'manuscript_title': manuscript.title,
                            'manuscript_id': manuscript.manuscript_id,
                            'volume': issue.volume,
                            'issue': issue.number,
                            'year': issue.year,
                            'doi': manuscript.doi,
                            'article_url': f"{settings.FRONTEND_URL}/articles/{manuscript.manuscript_id}"
                        }
                    )
                except Exception as e:
                    print(f"Failed to send email to {author.email}: {e}")

    db.refresh(issue)
    return issue


@router.get("/statistics/overview", response_model=IssueStatistics)
@require_role([UserRole.EDITOR_IN_CHIEF, UserRole.ASSOCIATE_EDITOR, UserRole.ADMIN])
async def get_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get overview statistics for issue management."""

    total_issues = db.query(Issue).count()
    published_issues = db.query(Issue).filter(Issue.is_published == True).count()

    now = datetime.now()
    scheduled_issues = db.query(Issue).filter(
        and_(
            Issue.is_published == False,
            Issue.scheduled_publication.isnot(None)
        )
    ).count()

    current_year = now.year
    current_year_issues = db.query(Issue).filter(Issue.year == current_year).count()

    # Get current issue (latest published or scheduled)
    current_issue = db.query(Issue).filter(
        or_(
            Issue.is_published == True,
            Issue.scheduled_publication.isnot(None)
        )
    ).order_by(
        Issue.year.desc(),
        Issue.volume.desc(),
        Issue.number.desc()
    ).first()

    if current_issue:
        articles_in_current = db.query(Manuscript).filter(
            and_(
                Manuscript.volume == current_issue.volume,
                Manuscript.issue == current_issue.number
            )
        ).count()
    else:
        articles_in_current = 0

    # Count accepted manuscripts not yet assigned to issue
    unpublished_accepted = db.query(Manuscript).filter(
        and_(
            Manuscript.status.in_([ManuscriptStatus.ACCEPTED, ManuscriptStatus.IN_PRODUCTION]),
            Manuscript.volume.is_(None),
            Manuscript.issue.is_(None)
        )
    ).count()

    return IssueStatistics(
        total_issues=total_issues,
        published_issues=published_issues,
        scheduled_issues=scheduled_issues,
        current_year_issues=current_year_issues,
        articles_in_current_issue=articles_in_current,
        unpublished_accepted_articles=unpublished_accepted
    )


@router.delete("/{issue_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_role([UserRole.EDITOR_IN_CHIEF, UserRole.ADMIN])
async def delete_issue(
    issue_id: int,
    force: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an issue.

    Cannot delete published issues unless force=True.
    Removes issue assignment from all manuscripts in issue.
    """
    issue = db.query(Issue).filter(Issue.id == issue_id).first()

    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue not found"
        )

    if issue.is_published and not force:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete published issue. Use force=True to override."
        )

    # Unassign all manuscripts
    manuscripts = db.query(Manuscript).filter(
        and_(
            Manuscript.volume == issue.volume,
            Manuscript.issue == issue.number
        )
    ).all()

    for manuscript in manuscripts:
        manuscript.volume = None
        manuscript.issue = None
        manuscript.article_order = None
        if issue.is_published:
            manuscript.status = ManuscriptStatus.IN_PRODUCTION

    db.delete(issue)
    db.commit()

    return None
