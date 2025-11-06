"""
Copyediting workflow API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime, timedelta
import os
import shutil

from db.base import get_db
from db.models import (
    User,
    Manuscript,
    ManuscriptStatus,
    UserRole,
    CopyeditingAssignment,
    ManuscriptFile
)
from schemas.copyediting import (
    CopyeditingAssignmentCreate,
    CopyeditingAssignmentResponse,
    CopyeditingAssignmentUpdate,
    CopyeditingFileUpload,
    AuthorReviewRequest,
    AuthorReviewResponse,
    CopyeditingStatistics,
    CopyeditingAssignmentList
)
from api.auth import get_current_user
from api.users import require_role
from services.email_service import email_service
from core.config import settings

router = APIRouter()


def check_assignment_access(
    assignment: CopyeditingAssignment,
    user: User,
    require_copyeditor: bool = False
) -> None:
    """
    Check if user has access to this assignment.

    Args:
        assignment: The copyediting assignment
        user: Current user
        require_copyeditor: If True, requires user to be the assigned copyeditor

    Raises:
        HTTPException: If user doesn't have access
    """
    is_editor = user.role in [UserRole.EDITOR_IN_CHIEF, UserRole.ASSOCIATE_EDITOR]
    is_assigned_copyeditor = assignment.copyeditor_id == user.id

    if require_copyeditor and not is_assigned_copyeditor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the assigned copyeditor can perform this action"
        )

    if not (is_editor or is_assigned_copyeditor):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this assignment"
        )


@router.get("/", response_model=CopyeditingAssignmentList)
async def list_assignments(
    status_filter: Optional[str] = None,
    manuscript_id: Optional[int] = None,
    copyeditor_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List copyediting assignments with filtering and pagination.

    - Editors see all assignments
    - Copyeditors see only their assignments
    - Authors see assignments for their manuscripts
    """
    query = db.query(CopyeditingAssignment)

    # Access control
    if current_user.role == UserRole.COPYEDITOR:
        query = query.filter(CopyeditingAssignment.copyeditor_id == current_user.id)
    elif current_user.role == UserRole.AUTHOR:
        # Get manuscripts where user is author
        author_manuscripts = db.query(Manuscript).filter(
            Manuscript.submitter_id == current_user.id
        ).all()
        manuscript_ids = [m.id for m in author_manuscripts]
        query = query.filter(CopyeditingAssignment.manuscript_id.in_(manuscript_ids))
    elif current_user.role not in [UserRole.EDITOR_IN_CHIEF, UserRole.ASSOCIATE_EDITOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view assignments"
        )

    # Apply filters
    if status_filter:
        query = query.filter(CopyeditingAssignment.status == status_filter)
    if manuscript_id:
        query = query.filter(CopyeditingAssignment.manuscript_id == manuscript_id)
    if copyeditor_id:
        query = query.filter(CopyeditingAssignment.copyeditor_id == copyeditor_id)

    # Count total
    total = query.count()

    # Pagination
    offset = (page - 1) * page_size
    assignments = query.order_by(CopyeditingAssignment.assigned_at.desc()).offset(offset).limit(page_size).all()

    # Enrich with copyeditor and manuscript info
    response_assignments = []
    for assignment in assignments:
        copyeditor = db.query(User).filter(User.id == assignment.copyeditor_id).first()
        manuscript = db.query(Manuscript).filter(Manuscript.id == assignment.manuscript_id).first()

        assignment_dict = CopyeditingAssignmentResponse.from_orm(assignment).dict()
        assignment_dict['copyeditor_name'] = f"{copyeditor.first_name} {copyeditor.last_name}" if copyeditor else None
        assignment_dict['manuscript_title'] = manuscript.title if manuscript else None

        response_assignments.append(CopyeditingAssignmentResponse(**assignment_dict))

    return CopyeditingAssignmentList(
        total=total,
        assignments=response_assignments,
        page=page,
        page_size=page_size
    )


@router.post("/", response_model=CopyeditingAssignmentResponse, status_code=status.HTTP_201_CREATED)
@require_role([UserRole.EDITOR_IN_CHIEF, UserRole.ASSOCIATE_EDITOR])
async def create_assignment(
    assignment_data: CopyeditingAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new copyediting assignment.

    Requirements:
    - Manuscript must be in ACCEPTED status
    - Copyeditor must have COPYEDITOR role
    - Sends email notification to copyeditor
    """
    # Verify manuscript exists and is accepted
    manuscript = db.query(Manuscript).filter(Manuscript.id == assignment_data.manuscript_id).first()
    if not manuscript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manuscript not found"
        )

    if manuscript.status != ManuscriptStatus.ACCEPTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Manuscript must be in ACCEPTED status (current: {manuscript.status})"
        )

    # Check if assignment already exists
    existing = db.query(CopyeditingAssignment).filter(
        and_(
            CopyeditingAssignment.manuscript_id == assignment_data.manuscript_id,
            CopyeditingAssignment.status.in_(['pending', 'in_progress', 'awaiting_author_review'])
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An active copyediting assignment already exists for this manuscript"
        )

    # Verify copyeditor exists and has correct role
    copyeditor = db.query(User).filter(User.id == assignment_data.copyeditor_id).first()
    if not copyeditor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Copyeditor not found"
        )

    if copyeditor.role != UserRole.COPYEDITOR:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Assigned user must have COPYEDITOR role"
        )

    # Get original manuscript file
    original_file = db.query(ManuscriptFile).filter(
        and_(
            ManuscriptFile.manuscript_id == manuscript.id,
            ManuscriptFile.file_type == 'manuscript',
            ManuscriptFile.version == manuscript.version
        )
    ).order_by(ManuscriptFile.uploaded_at.desc()).first()

    # Create assignment
    new_assignment = CopyeditingAssignment(
        manuscript_id=assignment_data.manuscript_id,
        copyeditor_id=assignment_data.copyeditor_id,
        assigned_by_id=current_user.id,
        original_file_id=original_file.id if original_file else None,
        notes=assignment_data.notes,
        due_date=assignment_data.due_date,
        status='pending',
        assigned_at=datetime.now()
    )

    db.add(new_assignment)

    # Update manuscript status
    manuscript.status = ManuscriptStatus.COPYEDITING

    db.commit()
    db.refresh(new_assignment)

    # Send email notification to copyeditor
    try:
        await email_service.send_email(
            recipients=[copyeditor.email],
            subject=f"New Copyediting Assignment: {manuscript.title}",
            template_name="copyediting_assignment",
            context={
                'copyeditor_name': f"{copyeditor.first_name} {copyeditor.last_name}",
                'manuscript_title': manuscript.title,
                'manuscript_id': manuscript.manuscript_id,
                'due_date': assignment_data.due_date.strftime('%Y-%m-%d') if assignment_data.due_date else 'Not specified',
                'notes': assignment_data.notes or '',
                'dashboard_url': f"{settings.FRONTEND_URL}/copyediting"
            }
        )
    except Exception as e:
        # Log error but don't fail the request
        print(f"Failed to send email: {e}")

    return new_assignment


@router.get("/{assignment_id}", response_model=CopyeditingAssignmentResponse)
async def get_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get details of a specific copyediting assignment."""
    assignment = db.query(CopyeditingAssignment).filter(
        CopyeditingAssignment.id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )

    check_assignment_access(assignment, current_user)

    # Enrich with additional data
    copyeditor = db.query(User).filter(User.id == assignment.copyeditor_id).first()
    manuscript = db.query(Manuscript).filter(Manuscript.id == assignment.manuscript_id).first()

    assignment_dict = CopyeditingAssignmentResponse.from_orm(assignment).dict()
    assignment_dict['copyeditor_name'] = f"{copyeditor.first_name} {copyeditor.last_name}" if copyeditor else None
    assignment_dict['manuscript_title'] = manuscript.title if manuscript else None

    return CopyeditingAssignmentResponse(**assignment_dict)


@router.patch("/{assignment_id}", response_model=CopyeditingAssignmentResponse)
@require_role([UserRole.EDITOR_IN_CHIEF, UserRole.ASSOCIATE_EDITOR])
async def update_assignment(
    assignment_id: int,
    update_data: CopyeditingAssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update copyediting assignment details (editors only)."""
    assignment = db.query(CopyeditingAssignment).filter(
        CopyeditingAssignment.id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )

    # Update fields
    if update_data.notes is not None:
        assignment.notes = update_data.notes
    if update_data.internal_notes is not None:
        assignment.internal_notes = update_data.internal_notes
    if update_data.due_date is not None:
        assignment.due_date = update_data.due_date
    if update_data.status is not None:
        assignment.status = update_data.status

    db.commit()
    db.refresh(assignment)

    return assignment


@router.post("/{assignment_id}/start", response_model=CopyeditingAssignmentResponse)
async def start_copyediting(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark assignment as started by copyeditor.
    Updates status from 'pending' to 'in_progress'.
    """
    assignment = db.query(CopyeditingAssignment).filter(
        CopyeditingAssignment.id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )

    check_assignment_access(assignment, current_user, require_copyeditor=True)

    if assignment.status != 'pending':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot start assignment in status: {assignment.status}"
        )

    assignment.status = 'in_progress'
    assignment.started_at = datetime.now()

    db.commit()
    db.refresh(assignment)

    return assignment


@router.post("/{assignment_id}/upload", response_model=CopyeditingAssignmentResponse)
async def upload_copyedited_file(
    assignment_id: int,
    file: UploadFile = File(...),
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload copyedited manuscript file.
    Can be called multiple times to update the copyedited version.
    """
    assignment = db.query(CopyeditingAssignment).filter(
        CopyeditingAssignment.id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )

    check_assignment_access(assignment, current_user, require_copyeditor=True)

    # If not started, start it now
    if assignment.status == 'pending':
        assignment.status = 'in_progress'
        assignment.started_at = datetime.now()

    # Validate file type
    allowed_extensions = ['.docx', '.doc', '.pdf', '.tex']
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_ext} not allowed. Allowed: {', '.join(allowed_extensions)}"
        )

    # Save file
    manuscript = db.query(Manuscript).filter(Manuscript.id == assignment.manuscript_id).first()
    upload_dir = f"{settings.UPLOAD_DIR}/manuscripts/{manuscript.manuscript_id}/copyedited"
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create file record
    manuscript_file = ManuscriptFile(
        manuscript_id=manuscript.id,
        file_type='copyedited',
        file_name=file.filename,
        file_path=file_path,
        file_size=os.path.getsize(file_path),
        uploaded_by_id=current_user.id,
        version=manuscript.version
    )

    db.add(manuscript_file)
    db.flush()

    # Update assignment
    assignment.copyedited_file_id = manuscript_file.id
    if notes:
        assignment.notes = notes

    db.commit()
    db.refresh(assignment)

    return assignment


@router.post("/{assignment_id}/request-author-review", response_model=CopyeditingAssignmentResponse)
async def request_author_review(
    assignment_id: int,
    request_data: AuthorReviewRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Request author review of copyedited manuscript.
    Requires copyedited file to be uploaded.
    """
    assignment = db.query(CopyeditingAssignment).filter(
        CopyeditingAssignment.id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )

    check_assignment_access(assignment, current_user, require_copyeditor=True)

    if not assignment.copyedited_file_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must upload copyedited file before requesting author review"
        )

    # Update status
    assignment.status = 'awaiting_author_review'
    assignment.notes = request_data.notes_to_author

    db.commit()
    db.refresh(assignment)

    # Send email to author
    manuscript = db.query(Manuscript).filter(Manuscript.id == assignment.manuscript_id).first()
    author = db.query(User).filter(User.id == manuscript.submitter_id).first()

    if author:
        try:
            await email_service.send_email(
                recipients=[author.email],
                subject=f"Copyedited Manuscript Ready for Review: {manuscript.title}",
                template_name="copyediting_author_review",
                context={
                    'author_name': f"{author.first_name} {author.last_name}",
                    'manuscript_title': manuscript.title,
                    'manuscript_id': manuscript.manuscript_id,
                    'notes': request_data.notes_to_author,
                    'review_url': f"{settings.FRONTEND_URL}/manuscripts/{manuscript.id}/copyediting"
                }
            )
        except Exception as e:
            print(f"Failed to send email: {e}")

    return assignment


@router.post("/{assignment_id}/author-review", response_model=CopyeditingAssignmentResponse)
async def submit_author_review(
    assignment_id: int,
    review_data: AuthorReviewResponse,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Author's response to copyedited manuscript.
    Can approve or request changes.
    """
    assignment = db.query(CopyeditingAssignment).filter(
        CopyeditingAssignment.id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )

    # Verify user is the manuscript author
    manuscript = db.query(Manuscript).filter(Manuscript.id == assignment.manuscript_id).first()
    if manuscript.submitter_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the manuscript author can review copyediting"
        )

    if assignment.status != 'awaiting_author_review':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Assignment is not awaiting author review (current status: {assignment.status})"
        )

    # Update assignment
    assignment.author_approved = review_data.approved
    assignment.author_notes = review_data.notes
    assignment.author_reviewed_at = datetime.now()

    if review_data.approved:
        assignment.status = 'author_approved'
    else:
        assignment.status = 'author_requested_changes'
        assignment.notes = review_data.requested_changes or review_data.notes

    db.commit()
    db.refresh(assignment)

    # Notify copyeditor
    copyeditor = db.query(User).filter(User.id == assignment.copyeditor_id).first()
    if copyeditor:
        try:
            await email_service.send_email(
                recipients=[copyeditor.email],
                subject=f"Author Review Complete: {manuscript.title}",
                template_name="copyediting_author_response",
                context={
                    'copyeditor_name': f"{copyeditor.first_name} {copyeditor.last_name}",
                    'manuscript_title': manuscript.title,
                    'approved': review_data.approved,
                    'notes': review_data.notes or '',
                    'dashboard_url': f"{settings.FRONTEND_URL}/copyediting/{assignment.id}"
                }
            )
        except Exception as e:
            print(f"Failed to send email: {e}")

    return assignment


@router.post("/{assignment_id}/complete", response_model=CopyeditingAssignmentResponse)
@require_role([UserRole.EDITOR_IN_CHIEF, UserRole.ASSOCIATE_EDITOR])
async def complete_copyediting(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark copyediting as complete and move manuscript to production.
    Requires author approval or editor override.
    """
    assignment = db.query(CopyeditingAssignment).filter(
        CopyeditingAssignment.id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )

    if not assignment.copyedited_file_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Copyedited file must be uploaded before completing"
        )

    # Update assignment
    assignment.status = 'completed'
    assignment.completed_at = datetime.now()

    # Update manuscript status
    manuscript = db.query(Manuscript).filter(Manuscript.id == assignment.manuscript_id).first()
    manuscript.status = ManuscriptStatus.IN_PRODUCTION

    db.commit()
    db.refresh(assignment)

    return assignment


@router.get("/statistics/overview", response_model=CopyeditingStatistics)
@require_role([UserRole.EDITOR_IN_CHIEF, UserRole.ASSOCIATE_EDITOR, UserRole.ADMIN])
async def get_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get overview statistics for copyediting workflow."""

    total = db.query(CopyeditingAssignment).count()

    pending = db.query(CopyeditingAssignment).filter(
        CopyeditingAssignment.status == 'pending'
    ).count()

    in_progress = db.query(CopyeditingAssignment).filter(
        CopyeditingAssignment.status == 'in_progress'
    ).count()

    completed = db.query(CopyeditingAssignment).filter(
        CopyeditingAssignment.status == 'completed'
    ).count()

    awaiting_review = db.query(CopyeditingAssignment).filter(
        CopyeditingAssignment.status == 'awaiting_author_review'
    ).count()

    # Calculate average completion time
    completed_assignments = db.query(CopyeditingAssignment).filter(
        and_(
            CopyeditingAssignment.status == 'completed',
            CopyeditingAssignment.assigned_at.isnot(None),
            CopyeditingAssignment.completed_at.isnot(None)
        )
    ).all()

    if completed_assignments:
        total_days = sum([
            (a.completed_at - a.assigned_at).days
            for a in completed_assignments
        ])
        avg_days = total_days / len(completed_assignments)
    else:
        avg_days = None

    # Count overdue
    now = datetime.now()
    overdue = db.query(CopyeditingAssignment).filter(
        and_(
            CopyeditingAssignment.due_date < now,
            CopyeditingAssignment.status.in_(['pending', 'in_progress', 'awaiting_author_review'])
        )
    ).count()

    return CopyeditingStatistics(
        total_assignments=total,
        pending_assignments=pending,
        in_progress_assignments=in_progress,
        completed_assignments=completed,
        awaiting_author_review=awaiting_review,
        average_completion_days=avg_days,
        overdue_assignments=overdue
    )


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_role([UserRole.EDITOR_IN_CHIEF, UserRole.ADMIN])
async def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a copyediting assignment (admin/editor only).
    Should only be used for mistakes. Does not delete uploaded files.
    """
    assignment = db.query(CopyeditingAssignment).filter(
        CopyeditingAssignment.id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )

    # Revert manuscript status if needed
    manuscript = db.query(Manuscript).filter(Manuscript.id == assignment.manuscript_id).first()
    if manuscript.status == ManuscriptStatus.COPYEDITING:
        manuscript.status = ManuscriptStatus.ACCEPTED

    db.delete(assignment)
    db.commit()

    return None
