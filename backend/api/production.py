"""
Production workflow API endpoints.

Handles:
- Layout editing assignments
- Proofreading assignments
- Galley generation (PDF, HTML, EPUB, XML)
- Production tracking
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import datetime
import os
import shutil
import subprocess

from db.base import get_db
from db.models import (
    User,
    Manuscript,
    ManuscriptStatus,
    UserRole,
    ProductionAssignment,
    ManuscriptFile
)
from schemas.production import (
    ProductionAssignmentCreate,
    ProductionAssignmentResponse,
    ProductionAssignmentUpdate,
    GalleyGenerationRequest,
    GalleyResponse,
    ProductionStatistics,
    ProductionAssignmentList,
    ManuscriptGalleyList
)
from api.auth import get_current_user
from api.users import require_role
from services.email_service import email_service
from core.config import settings

router = APIRouter()


def check_production_access(
    assignment: ProductionAssignment,
    user: User,
    require_assigned: bool = False
) -> None:
    """Check if user has access to this production assignment."""
    is_editor = user.role in [UserRole.EDITOR_IN_CHIEF, UserRole.ASSOCIATE_EDITOR]
    is_assigned = assignment.assigned_to_id == user.id

    if require_assigned and not is_assigned:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the assigned person can perform this action"
        )

    if not (is_editor or is_assigned):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this assignment"
        )


@router.get("/", response_model=ProductionAssignmentList)
async def list_assignments(
    status_filter: Optional[str] = None,
    manuscript_id: Optional[int] = None,
    task_type: Optional[str] = None,
    assigned_to_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List production assignments with filtering and pagination.

    - Editors see all assignments
    - Production staff see only their assignments
    """
    query = db.query(ProductionAssignment)

    # Access control
    if current_user.role in [UserRole.LAYOUT_EDITOR, UserRole.PROOFREADER]:
        query = query.filter(ProductionAssignment.assigned_to_id == current_user.id)
    elif current_user.role not in [UserRole.EDITOR_IN_CHIEF, UserRole.ASSOCIATE_EDITOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view production assignments"
        )

    # Apply filters
    if status_filter:
        query = query.filter(ProductionAssignment.status == status_filter)
    if manuscript_id:
        query = query.filter(ProductionAssignment.manuscript_id == manuscript_id)
    if task_type:
        query = query.filter(ProductionAssignment.task_type == task_type)
    if assigned_to_id:
        query = query.filter(ProductionAssignment.assigned_to_id == assigned_to_id)

    # Count total
    total = query.count()

    # Pagination
    offset = (page - 1) * page_size
    assignments = query.order_by(ProductionAssignment.assigned_at.desc()).offset(offset).limit(page_size).all()

    # Enrich with user and manuscript info
    response_assignments = []
    for assignment in assignments:
        assigned_to = db.query(User).filter(User.id == assignment.assigned_to_id).first()
        manuscript = db.query(Manuscript).filter(Manuscript.id == assignment.manuscript_id).first()

        assignment_dict = ProductionAssignmentResponse.from_orm(assignment).dict()
        assignment_dict['assigned_to_name'] = f"{assigned_to.first_name} {assigned_to.last_name}" if assigned_to else None
        assignment_dict['manuscript_title'] = manuscript.title if manuscript else None

        response_assignments.append(ProductionAssignmentResponse(**assignment_dict))

    return ProductionAssignmentList(
        total=total,
        assignments=response_assignments,
        page=page,
        page_size=page_size
    )


@router.post("/", response_model=ProductionAssignmentResponse, status_code=status.HTTP_201_CREATED)
@require_role([UserRole.EDITOR_IN_CHIEF, UserRole.ASSOCIATE_EDITOR])
async def create_assignment(
    assignment_data: ProductionAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new production assignment.

    Task types:
    - layout: Layout editing
    - proofreading: Proofreading
    - galley_conversion: Convert to publication formats
    """
    # Verify manuscript exists and is in production
    manuscript = db.query(Manuscript).filter(Manuscript.id == assignment_data.manuscript_id).first()
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

    # Verify assigned user exists and has appropriate role
    assigned_user = db.query(User).filter(User.id == assignment_data.assigned_to_id).first()
    if not assigned_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assigned user not found"
        )

    # Check role matches task type
    role_task_map = {
        'layout': UserRole.LAYOUT_EDITOR,
        'proofreading': UserRole.PROOFREADER,
        'galley_conversion': [UserRole.LAYOUT_EDITOR, UserRole.EDITOR_IN_CHIEF, UserRole.ASSOCIATE_EDITOR]
    }

    expected_roles = role_task_map.get(assignment_data.task_type)
    if isinstance(expected_roles, list):
        if assigned_user.role not in expected_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User must have one of these roles: {expected_roles}"
            )
    elif assigned_user.role != expected_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User must have {expected_roles} role for {assignment_data.task_type} tasks"
        )

    # Get source file (copyedited version)
    source_file = db.query(ManuscriptFile).filter(
        and_(
            ManuscriptFile.manuscript_id == manuscript.id,
            ManuscriptFile.file_type == 'copyedited'
        )
    ).order_by(ManuscriptFile.uploaded_at.desc()).first()

    # Create assignment
    new_assignment = ProductionAssignment(
        manuscript_id=assignment_data.manuscript_id,
        assigned_to_id=assignment_data.assigned_to_id,
        assigned_by_id=current_user.id,
        task_type=assignment_data.task_type,
        galley_format=assignment_data.galley_format,
        galley_label=assignment_data.galley_label,
        source_file_id=source_file.id if source_file else None,
        due_date=assignment_data.due_date,
        status='pending',
        notes=assignment_data.notes,
        assigned_at=datetime.now()
    )

    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)

    # Send email notification
    try:
        await email_service.send_email(
            recipients=[assigned_user.email],
            subject=f"New Production Assignment: {manuscript.title}",
            template_name="production_assignment",
            context={
                'user_name': f"{assigned_user.first_name} {assigned_user.last_name}",
                'task_type': assignment_data.task_type,
                'manuscript_title': manuscript.title,
                'manuscript_id': manuscript.manuscript_id,
                'due_date': assignment_data.due_date.strftime('%Y-%m-%d') if assignment_data.due_date else 'Not specified',
                'notes': assignment_data.notes or '',
                'dashboard_url': f"{settings.FRONTEND_URL}/production"
            }
        )
    except Exception as e:
        print(f"Failed to send email: {e}")

    return new_assignment


@router.get("/{assignment_id}", response_model=ProductionAssignmentResponse)
async def get_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get details of a specific production assignment."""
    assignment = db.query(ProductionAssignment).filter(
        ProductionAssignment.id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )

    check_production_access(assignment, current_user)

    # Enrich with additional data
    assigned_to = db.query(User).filter(User.id == assignment.assigned_to_id).first()
    manuscript = db.query(Manuscript).filter(Manuscript.id == assignment.manuscript_id).first()

    assignment_dict = ProductionAssignmentResponse.from_orm(assignment).dict()
    assignment_dict['assigned_to_name'] = f"{assigned_to.first_name} {assigned_to.last_name}" if assigned_to else None
    assignment_dict['manuscript_title'] = manuscript.title if manuscript else None

    return ProductionAssignmentResponse(**assignment_dict)


@router.patch("/{assignment_id}", response_model=ProductionAssignmentResponse)
async def update_assignment(
    assignment_id: int,
    update_data: ProductionAssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update production assignment."""
    assignment = db.query(ProductionAssignment).filter(
        ProductionAssignment.id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )

    check_production_access(assignment, current_user)

    # Update fields
    if update_data.status is not None:
        assignment.status = update_data.status
        if update_data.status == 'in_progress' and not assignment.started_at:
            assignment.started_at = datetime.now()
        elif update_data.status == 'completed' and not assignment.completed_at:
            assignment.completed_at = datetime.now()

    if update_data.due_date is not None:
        assignment.due_date = update_data.due_date
    if update_data.notes is not None:
        assignment.notes = update_data.notes

    db.commit()
    db.refresh(assignment)

    return assignment


@router.post("/{assignment_id}/upload", response_model=ProductionAssignmentResponse)
async def upload_output_file(
    assignment_id: int,
    file: UploadFile = File(...),
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload output file for production assignment."""
    assignment = db.query(ProductionAssignment).filter(
        ProductionAssignment.id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )

    check_production_access(assignment, current_user, require_assigned=True)

    # Start assignment if pending
    if assignment.status == 'pending':
        assignment.status = 'in_progress'
        assignment.started_at = datetime.now()

    # Validate file type based on task
    allowed_extensions = {
        'layout': ['.docx', '.doc', '.pdf', '.indd'],
        'proofreading': ['.docx', '.doc', '.pdf'],
        'galley_conversion': ['.pdf', '.html', '.xml', '.epub']
    }

    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions.get(assignment.task_type, []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_ext} not allowed for {assignment.task_type}"
        )

    # Save file
    manuscript = db.query(Manuscript).filter(Manuscript.id == assignment.manuscript_id).first()
    upload_dir = f"{settings.UPLOAD_DIR}/manuscripts/{manuscript.manuscript_id}/production"
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Create file record
    manuscript_file = ManuscriptFile(
        manuscript_id=manuscript.id,
        file_type=f'production_{assignment.task_type}',
        file_name=file.filename,
        file_path=file_path,
        file_size=os.path.getsize(file_path),
        uploaded_by_id=current_user.id,
        version=manuscript.version
    )

    db.add(manuscript_file)
    db.flush()

    # Update assignment
    assignment.output_file_id = manuscript_file.id
    if notes:
        assignment.notes = notes

    db.commit()
    db.refresh(assignment)

    return assignment


@router.post("/{assignment_id}/complete", response_model=ProductionAssignmentResponse)
async def complete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark production assignment as complete."""
    assignment = db.query(ProductionAssignment).filter(
        ProductionAssignment.id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )

    check_production_access(assignment, current_user, require_assigned=True)

    if not assignment.output_file_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must upload output file before completing assignment"
        )

    assignment.status = 'completed'
    assignment.completed_at = datetime.now()

    db.commit()
    db.refresh(assignment)

    # Notify editor
    editor = db.query(User).filter(User.id == assignment.assigned_by_id).first()
    manuscript = db.query(Manuscript).filter(Manuscript.id == assignment.manuscript_id).first()

    if editor:
        try:
            await email_service.send_email(
                recipients=[editor.email],
                subject=f"Production Task Complete: {manuscript.title}",
                template_name="production_complete",
                context={
                    'editor_name': f"{editor.first_name} {editor.last_name}",
                    'task_type': assignment.task_type,
                    'manuscript_title': manuscript.title,
                    'manuscript_id': manuscript.manuscript_id,
                    'dashboard_url': f"{settings.FRONTEND_URL}/production/{assignment.id}"
                }
            )
        except Exception as e:
            print(f"Failed to send email: {e}")

    return assignment


@router.post("/manuscripts/{manuscript_id}/galleys/generate", response_model=GalleyResponse)
@require_role([UserRole.EDITOR_IN_CHIEF, UserRole.ASSOCIATE_EDITOR, UserRole.LAYOUT_EDITOR])
async def generate_galley(
    manuscript_id: int,
    galley_request: GalleyGenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Generate galley files automatically from manuscript.

    Supports:
    - PDF (via WeasyPrint from HTML)
    - HTML (from DOCX/LaTeX)
    - XML (JATS format)
    - EPUB (via Pandoc)

    Note: Requires external tools to be installed.
    """
    manuscript = db.query(Manuscript).filter(Manuscript.id == manuscript_id).first()
    if not manuscript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manuscript not found"
        )

    # Get latest copyedited or production file
    source_file = db.query(ManuscriptFile).filter(
        and_(
            ManuscriptFile.manuscript_id == manuscript.id,
            ManuscriptFile.file_type.in_(['copyedited', 'production_layout'])
        )
    ).order_by(ManuscriptFile.uploaded_at.desc()).first()

    if not source_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No source file available for galley generation"
        )

    # Output directory
    output_dir = f"{settings.UPLOAD_DIR}/manuscripts/{manuscript.manuscript_id}/galleys"
    os.makedirs(output_dir, exist_ok=True)

    # Generate based on format
    output_filename = f"{manuscript.manuscript_id}_galley.{galley_request.format}"
    output_path = os.path.join(output_dir, output_filename)

    try:
        if galley_request.format == 'pdf':
            # Use pandoc or weasyprint for PDF generation
            subprocess.run([
                'pandoc',
                source_file.file_path,
                '-o', output_path,
                '--pdf-engine=xelatex'
            ], check=True)

        elif galley_request.format == 'html':
            # Convert to HTML
            subprocess.run([
                'pandoc',
                source_file.file_path,
                '-o', output_path,
                '--standalone',
                '--metadata', f'title={manuscript.title}'
            ], check=True)

        elif galley_request.format == 'epub':
            # Convert to EPUB
            subprocess.run([
                'pandoc',
                source_file.file_path,
                '-o', output_path,
                '--metadata', f'title={manuscript.title}',
                '--metadata', f'author={manuscript.submitter_id}'
            ], check=True)

        elif galley_request.format == 'xml':
            # Generate JATS XML (simplified - would need more complex processing)
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="XML galley generation requires additional configuration"
            )

    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Galley generation failed: {str(e)}"
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Required tool not installed. Please install pandoc."
        )

    # Create file record
    galley_label = galley_request.label or f"{galley_request.format.upper()} Galley"

    galley_file = ManuscriptFile(
        manuscript_id=manuscript.id,
        file_type='galley',
        file_name=output_filename,
        file_path=output_path,
        file_size=os.path.getsize(output_path),
        uploaded_by_id=current_user.id,
        version=manuscript.version,
        galley_label=galley_label,
        galley_format=galley_request.format
    )

    db.add(galley_file)
    db.commit()
    db.refresh(galley_file)

    return GalleyResponse(
        id=galley_file.id,
        manuscript_id=manuscript.id,
        format=galley_request.format,
        label=galley_label,
        file_path=output_path,
        file_size=galley_file.file_size,
        generated_at=galley_file.uploaded_at,
        version=manuscript.version
    )


@router.get("/manuscripts/{manuscript_id}/galleys", response_model=ManuscriptGalleyList)
async def list_galleys(
    manuscript_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all galley files for a manuscript."""
    manuscript = db.query(Manuscript).filter(Manuscript.id == manuscript_id).first()
    if not manuscript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manuscript not found"
        )

    galleys = db.query(ManuscriptFile).filter(
        and_(
            ManuscriptFile.manuscript_id == manuscript.id,
            ManuscriptFile.file_type == 'galley'
        )
    ).order_by(ManuscriptFile.uploaded_at.desc()).all()

    galley_responses = [
        GalleyResponse(
            id=g.id,
            manuscript_id=g.manuscript_id,
            format=g.galley_format or 'unknown',
            label=g.galley_label or 'Galley',
            file_path=g.file_path,
            file_size=g.file_size,
            generated_at=g.uploaded_at,
            version=g.version
        )
        for g in galleys
    ]

    return ManuscriptGalleyList(
        manuscript_id=manuscript.id,
        manuscript_title=manuscript.title,
        galleys=galley_responses
    )


@router.get("/statistics/overview", response_model=ProductionStatistics)
@require_role([UserRole.EDITOR_IN_CHIEF, UserRole.ASSOCIATE_EDITOR, UserRole.ADMIN])
async def get_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get overview statistics for production workflow."""

    total = db.query(ProductionAssignment).count()
    pending = db.query(ProductionAssignment).filter(ProductionAssignment.status == 'pending').count()
    in_progress = db.query(ProductionAssignment).filter(ProductionAssignment.status == 'in_progress').count()
    completed = db.query(ProductionAssignment).filter(ProductionAssignment.status == 'completed').count()

    layout = db.query(ProductionAssignment).filter(ProductionAssignment.task_type == 'layout').count()
    proofreading = db.query(ProductionAssignment).filter(ProductionAssignment.task_type == 'proofreading').count()
    galley = db.query(ProductionAssignment).filter(ProductionAssignment.task_type == 'galley_conversion').count()

    # Calculate average completion time
    completed_assignments = db.query(ProductionAssignment).filter(
        and_(
            ProductionAssignment.status == 'completed',
            ProductionAssignment.assigned_at.isnot(None),
            ProductionAssignment.completed_at.isnot(None)
        )
    ).all()

    if completed_assignments:
        total_days = sum([(a.completed_at - a.assigned_at).days for a in completed_assignments])
        avg_days = total_days / len(completed_assignments)
    else:
        avg_days = None

    # Count overdue
    now = datetime.now()
    overdue = db.query(ProductionAssignment).filter(
        and_(
            ProductionAssignment.due_date < now,
            ProductionAssignment.status.in_(['pending', 'in_progress'])
        )
    ).count()

    return ProductionStatistics(
        total_assignments=total,
        pending_assignments=pending,
        in_progress_assignments=in_progress,
        completed_assignments=completed,
        layout_assignments=layout,
        proofreading_assignments=proofreading,
        galley_assignments=galley,
        overdue_assignments=overdue,
        average_completion_days=avg_days
    )


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_role([UserRole.EDITOR_IN_CHIEF, UserRole.ADMIN])
async def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a production assignment (admin/editor only)."""
    assignment = db.query(ProductionAssignment).filter(
        ProductionAssignment.id == assignment_id
    ).first()

    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )

    db.delete(assignment)
    db.commit()

    return None
