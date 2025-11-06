"""
Manuscript management API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import shutil

from db.base import get_db
from db.models import User, Manuscript, ManuscriptStatus, UserRole, manuscript_authors
from schemas.manuscript import (
    ManuscriptCreate,
    ManuscriptResponse,
    ManuscriptUpdate,
    ManuscriptSubmit,
    ManuscriptPublish
)
from api.auth import get_current_user
from api.users import require_role
from services.email_service import email_service
from core.config import settings

router = APIRouter()


def generate_manuscript_id(db: Session) -> str:
    """Generate unique manuscript ID."""
    from datetime import datetime
    year = datetime.now().year
    count = db.query(Manuscript).filter(
        Manuscript.manuscript_id.like(f'MS-{year}-%')
    ).count()
    return f'MS-{year}-{count + 1:04d}'


@router.post("/", response_model=ManuscriptResponse, status_code=status.HTTP_201_CREATED)
async def create_manuscript(
    manuscript_data: ManuscriptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new manuscript draft.
    """
    # Generate manuscript ID
    manuscript_id = generate_manuscript_id(db)

    # Create manuscript
    new_manuscript = Manuscript(
        manuscript_id=manuscript_id,
        title=manuscript_data.title,
        abstract=manuscript_data.abstract,
        keywords=manuscript_data.keywords,
        specialization_id=manuscript_data.specialization_id,
        article_type=manuscript_data.article_type,
        submitter_id=current_user.id,
        status=ManuscriptStatus.DRAFT
    )

    db.add(new_manuscript)
    db.flush()  # Get the ID without committing

    # Add authors
    for author_info in manuscript_data.authors:
        author = db.query(User).filter(User.id == author_info.user_id).first()
        if not author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Author with ID {author_info.user_id} not found"
            )

        # Add to association table
        stmt = manuscript_authors.insert().values(
            manuscript_id=new_manuscript.id,
            author_id=author_info.user_id,
            author_order=author_info.order,
            is_corresponding=author_info.is_corresponding
        )
        db.execute(stmt)

    db.commit()
    db.refresh(new_manuscript)

    return new_manuscript


@router.post("/{manuscript_id}/upload", status_code=status.HTTP_200_OK)
async def upload_manuscript_file(
    manuscript_id: int,
    file: UploadFile = File(...),
    file_type: str = "manuscript",  # manuscript, supplementary, figure
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload manuscript file, supplementary files, or figures.
    """
    manuscript = db.query(Manuscript).filter(Manuscript.id == manuscript_id).first()

    if not manuscript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manuscript not found"
        )

    # Check permissions
    is_author = any(author.id == current_user.id for author in manuscript.authors)
    if not is_author and manuscript.submitter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to upload files for this manuscript"
        )

    # Check file size
    if file.size and file.size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE} bytes"
        )

    # Create upload directory
    upload_dir = os.path.join(settings.UPLOAD_DIR, "manuscripts", manuscript.manuscript_id)
    os.makedirs(upload_dir, exist_ok=True)

    # Save file
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Update manuscript record
    if file_type == "manuscript":
        manuscript.manuscript_file = file_path
    elif file_type == "supplementary":
        if not manuscript.supplementary_files:
            manuscript.supplementary_files = []
        manuscript.supplementary_files.append(file_path)
    elif file_type == "figure":
        if not manuscript.figures:
            manuscript.figures = []
        manuscript.figures.append(file_path)

    db.commit()

    return {"message": "File uploaded successfully", "file_path": file_path}


@router.post("/{manuscript_id}/submit", response_model=ManuscriptResponse)
async def submit_manuscript(
    manuscript_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit manuscript for review.
    """
    manuscript = db.query(Manuscript).filter(Manuscript.id == manuscript_id).first()

    if not manuscript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manuscript not found"
        )

    # Check permissions
    if manuscript.submitter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the submitter can submit the manuscript"
        )

    # Validate manuscript is ready for submission
    if manuscript.status not in [ManuscriptStatus.DRAFT, ManuscriptStatus.REVISIONS_REQUIRED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Manuscript is not in a submittable state"
        )

    if not manuscript.manuscript_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Manuscript file must be uploaded before submission"
        )

    # Update status
    manuscript.status = ManuscriptStatus.SUBMITTED
    manuscript.submitted_at = datetime.utcnow()
    db.commit()
    db.refresh(manuscript)

    # Send confirmation email to author
    await email_service.send_submission_confirmation(
        user_email=current_user.email,
        manuscript_id=manuscript.manuscript_id,
        title=manuscript.title
    )

    # Notify editor
    editors = db.query(User).filter(
        User.role.in_([UserRole.EDITOR_IN_CHIEF, UserRole.ASSOCIATE_EDITOR]),
        User.is_active == True
    ).all()

    for editor in editors:
        await email_service.send_editor_new_submission(
            editor_email=editor.email,
            manuscript_id=manuscript.manuscript_id,
            title=manuscript.title
        )

    return manuscript


@router.get("/", response_model=List[ManuscriptResponse])
async def list_manuscripts(
    status: Optional[ManuscriptStatus] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List manuscripts. Filter based on user role.
    """
    query = db.query(Manuscript)

    # Filter based on role
    if current_user.role == UserRole.AUTHOR:
        # Authors see only their manuscripts
        query = query.join(manuscript_authors).filter(
            manuscript_authors.c.author_id == current_user.id
        )
    elif current_user.role == UserRole.REVIEWER:
        # Reviewers see manuscripts assigned to them (handled in reviews endpoint)
        # For now, return empty
        return []
    # Editors and admins see all manuscripts

    if status:
        query = query.filter(Manuscript.status == status)

    manuscripts = query.offset(skip).limit(limit).all()
    return manuscripts


@router.get("/{manuscript_id}", response_model=ManuscriptResponse)
async def get_manuscript(
    manuscript_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get manuscript details.
    """
    manuscript = db.query(Manuscript).filter(Manuscript.id == manuscript_id).first()

    if not manuscript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manuscript not found"
        )

    # Check permissions
    is_author = any(author.id == current_user.id for author in manuscript.authors)
    is_editor = current_user.role in [UserRole.EDITOR_IN_CHIEF, UserRole.ASSOCIATE_EDITOR, UserRole.ADMIN]

    if not is_author and not is_editor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this manuscript"
        )

    return manuscript


@router.put("/{manuscript_id}", response_model=ManuscriptResponse)
async def update_manuscript(
    manuscript_id: int,
    manuscript_update: ManuscriptUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update manuscript (draft only).
    """
    manuscript = db.query(Manuscript).filter(Manuscript.id == manuscript_id).first()

    if not manuscript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manuscript not found"
        )

    # Check permissions
    if manuscript.submitter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this manuscript"
        )

    # Can only update drafts
    if manuscript.status not in [ManuscriptStatus.DRAFT, ManuscriptStatus.REVISIONS_REQUIRED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only update draft manuscripts"
        )

    # Update fields
    update_data = manuscript_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(manuscript, field, value)

    db.commit()
    db.refresh(manuscript)

    return manuscript


@router.post("/{manuscript_id}/publish", response_model=ManuscriptResponse)
async def publish_manuscript(
    manuscript_id: int,
    publish_data: ManuscriptPublish,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.EDITOR_IN_CHIEF, UserRole.ADMIN]))
):
    """
    Publish accepted manuscript (editor only).
    """
    manuscript = db.query(Manuscript).filter(Manuscript.id == manuscript_id).first()

    if not manuscript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manuscript not found"
        )

    if manuscript.status != ManuscriptStatus.ACCEPTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only accepted manuscripts can be published"
        )

    # Update publication info
    manuscript.status = ManuscriptStatus.PUBLISHED
    manuscript.published_at = datetime.utcnow()
    manuscript.volume = publish_data.volume
    manuscript.issue = publish_data.issue
    manuscript.page_start = publish_data.page_start
    manuscript.page_end = publish_data.page_end

    # TODO: Generate DOI, JATS XML, PDF, HTML

    db.commit()
    db.refresh(manuscript)

    # Send publication notification to authors
    for author in manuscript.authors:
        await email_service.send_publication_notification(
            author_email=author.email,
            author_name=author.full_name,
            manuscript_id=manuscript.manuscript_id,
            title=manuscript.title,
            doi=manuscript.doi or "Pending",
            article_url=f"{settings.JOURNAL_URL}/article/{manuscript.manuscript_id}"
        )

    return manuscript
