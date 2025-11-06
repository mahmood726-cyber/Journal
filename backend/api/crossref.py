"""
Crossref DOI Management API

Handles DOI registration, updates, and status tracking with Crossref.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import json

from db.base import get_db
from db.models import Manuscript, User, UserRole, ManuscriptStatus
from db.models_doi import DOIDeposit, ManuscriptDOI, DOIDepositLog, DOIStatus
from api.auth import get_current_user
from services.crossref_xml_service import generate_crossref_xml_for_manuscript
from services.crossref_api_service import (
    CrossrefAPIService,
    CrossrefEnvironment,
    deposit_manuscript_doi
)
from core.config import settings

router = APIRouter()


@router.post("/manuscripts/{manuscript_id}/register-doi")
async def register_manuscript_doi(
    manuscript_id: int,
    background_tasks: BackgroundTasks,
    auto_assign: bool = False,
    environment: str = "test",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Register DOI for a published manuscript with Crossref.

    Args:
        manuscript_id: ID of the manuscript
        auto_assign: If True and no DOI exists, generate one automatically
        environment: "test" or "production" (use test for verification)

    Requires:
        - Editor/Admin role
        - Manuscript must be published
        - DOI must be assigned to manuscript

    Returns:
        Deposit information and status
    """
    # Check permissions
    if current_user.role not in [UserRole.EDITOR, UserRole.EDITOR_IN_CHIEF, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only editors can register DOIs"
        )

    # Fetch manuscript
    manuscript = db.query(Manuscript).filter(Manuscript.id == manuscript_id).first()

    if not manuscript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manuscript not found"
        )

    # Check if published
    if manuscript.status != ManuscriptStatus.PUBLISHED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only published manuscripts can have DOIs registered"
        )

    # Check if DOI exists
    if not manuscript.doi:
        if auto_assign:
            # Auto-generate DOI
            doi_prefix = getattr(settings, 'CROSSREF_DOI_PREFIX', '10.XXXX')
            doi_suffix = manuscript.manuscript_id
            manuscript.doi = f"{doi_prefix}/{doi_suffix}"
            db.commit()
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Manuscript does not have a DOI assigned. Use auto_assign=true to generate one."
            )

    # Check if already registered
    existing_doi_record = db.query(ManuscriptDOI).filter(
        ManuscriptDOI.manuscript_id == manuscript_id
    ).first()

    if existing_doi_record and existing_doi_record.status == DOIStatus.SUCCESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"DOI {manuscript.doi} is already registered. Use update endpoint to modify metadata."
        )

    # Prepare manuscript data for Crossref
    manuscript_data = _prepare_manuscript_data(manuscript)

    # Depositor info
    depositor_info = {
        'name': getattr(settings, 'CROSSREF_DEPOSITOR_NAME', 'Journal Depositor'),
        'email': getattr(settings, 'CROSSREF_DEPOSITOR_EMAIL', 'deposits@journal.com'),
        'registrant': getattr(settings, 'JOURNAL_TITLE', 'Diamond Open Access Journal')
    }

    # Journal metadata
    journal_metadata = {
        'title': getattr(settings, 'JOURNAL_TITLE', 'Diamond Open Access Journal'),
        'abbrev': getattr(settings, 'JOURNAL_ABBREV', 'Diamond OA J'),
        'issn': getattr(settings, 'JOURNAL_ISSN', '2XXX-XXXX'),
    }

    # Generate Crossref XML
    try:
        xml_content = generate_crossref_xml_for_manuscript(
            manuscript=manuscript_data,
            depositor_info=depositor_info,
            journal_metadata=journal_metadata
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate Crossref XML: {str(e)}"
        )

    # Create DOI deposit record
    deposit = DOIDeposit(
        batch_id=f"batch_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{manuscript_id}",
        manuscript_ids=json.dumps([manuscript_id]),
        status=DOIStatus.PENDING,
        xml_content=xml_content,
        deposited_by_id=current_user.id,
        environment=environment,
        records_total=1
    )
    db.add(deposit)
    db.commit()
    db.refresh(deposit)

    # Create or update manuscript DOI record
    if existing_doi_record:
        existing_doi_record.deposit_id = deposit.id
        existing_doi_record.status = DOIStatus.PENDING
    else:
        # Parse DOI into prefix and suffix
        doi_parts = manuscript.doi.split('/', 1)
        doi_prefix = doi_parts[0] if len(doi_parts) > 0 else ''
        doi_suffix = doi_parts[1] if len(doi_parts) > 1 else ''

        doi_record = ManuscriptDOI(
            manuscript_id=manuscript_id,
            doi=manuscript.doi,
            doi_url=f"https://doi.org/{manuscript.doi}",
            status=DOIStatus.PENDING,
            deposit_id=deposit.id,
            prefix=doi_prefix,
            suffix=doi_suffix
        )
        db.add(doi_record)

    db.commit()

    # Log the action
    log = DOIDepositLog(
        deposit_id=deposit.id,
        action="create",
        status_before=None,
        status_after=DOIStatus.PENDING.value,
        message="DOI deposit created",
        performed_by_id=current_user.id
    )
    db.add(log)
    db.commit()

    # Submit to Crossref in background
    background_tasks.add_task(
        _submit_to_crossref,
        deposit.id,
        xml_content,
        environment,
        db
    )

    return {
        "success": True,
        "message": "DOI registration initiated",
        "deposit_id": deposit.id,
        "batch_id": deposit.batch_id,
        "doi": manuscript.doi,
        "status": deposit.status,
        "environment": environment
    }


@router.get("/manuscripts/{manuscript_id}/doi-status")
async def get_doi_status(
    manuscript_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get DOI registration status for a manuscript.

    Returns:
        DOI status information including registration details
    """
    # Fetch manuscript
    manuscript = db.query(Manuscript).filter(Manuscript.id == manuscript_id).first()

    if not manuscript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manuscript not found"
        )

    # Check permissions
    is_editor = current_user.role in [UserRole.EDITOR, UserRole.EDITOR_IN_CHIEF, UserRole.ADMIN]
    is_author = any(author.id == current_user.id for author in manuscript.authors)

    if not is_editor and not is_author:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view DOI status"
        )

    # Get DOI record
    doi_record = db.query(ManuscriptDOI).filter(
        ManuscriptDOI.manuscript_id == manuscript_id
    ).first()

    if not doi_record:
        return {
            "manuscript_id": manuscript_id,
            "doi": manuscript.doi,
            "registered": False,
            "status": None,
            "message": "DOI not yet registered with Crossref"
        }

    # Get deposit info
    deposit_info = None
    if doi_record.deposit:
        deposit_info = {
            "batch_id": doi_record.deposit.batch_id,
            "status": doi_record.deposit.status,
            "submitted_at": doi_record.deposit.submitted_at.isoformat() if doi_record.deposit.submitted_at else None,
            "completed_at": doi_record.deposit.completed_at.isoformat() if doi_record.deposit.completed_at else None,
            "environment": doi_record.deposit.environment
        }

    return {
        "manuscript_id": manuscript_id,
        "doi": doi_record.doi,
        "doi_url": doi_record.doi_url,
        "registered": doi_record.status == DOIStatus.SUCCESS,
        "status": doi_record.status,
        "registered_at": doi_record.registered_at.isoformat() if doi_record.registered_at else None,
        "last_verified_at": doi_record.last_verified_at.isoformat() if doi_record.last_verified_at else None,
        "deposit": deposit_info,
        "message": doi_record.verification_message
    }


@router.post("/deposits/{deposit_id}/check-status")
async def check_deposit_status(
    deposit_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check the status of a DOI deposit with Crossref.

    Queries Crossref API for current status and updates local records.

    Requires editor/admin role.
    """
    # Check permissions
    if current_user.role not in [UserRole.EDITOR, UserRole.EDITOR_IN_CHIEF, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only editors can check deposit status"
        )

    # Get deposit record
    deposit = db.query(DOIDeposit).filter(DOIDeposit.id == deposit_id).first()

    if not deposit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deposit not found"
        )

    # Get Crossref credentials
    crossref_username = getattr(settings, 'CROSSREF_USERNAME', None)
    crossref_password = getattr(settings, 'CROSSREF_PASSWORD', None)

    if not crossref_username or not crossref_password:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Crossref credentials not configured"
        )

    # Initialize Crossref API
    env = CrossrefEnvironment.PRODUCTION if deposit.environment == "production" else CrossrefEnvironment.TEST
    api_service = CrossrefAPIService(
        username=crossref_username,
        password=crossref_password,
        environment=env
    )

    # Query batch status
    result = await api_service.query_batch_status(deposit.batch_id)

    if result['success']:
        # Update deposit record
        old_status = deposit.status
        deposit.status = result['status']
        deposit.records_total = result.get('records_total', deposit.records_total)
        deposit.records_success = result.get('records_success', 0)
        deposit.records_failed = result.get('records_failed', 0)
        deposit.records_warning = result.get('records_warning', 0)
        deposit.last_checked_at = datetime.utcnow()

        if deposit.status == DOIStatus.SUCCESS and not deposit.completed_at:
            deposit.completed_at = datetime.utcnow()

        # Log status check
        log = DOIDepositLog(
            deposit_id=deposit.id,
            action="check_status",
            status_before=old_status.value if old_status else None,
            status_after=deposit.status.value,
            message="Status checked via Crossref API",
            response_data=json.dumps(result),
            performed_by_id=current_user.id
        )
        db.add(log)
        db.commit()

        return {
            "success": True,
            "deposit_id": deposit.id,
            "batch_id": deposit.batch_id,
            "status": deposit.status,
            "records_total": deposit.records_total,
            "records_success": deposit.records_success,
            "records_failed": deposit.records_failed,
            "records_warning": deposit.records_warning,
            "last_checked_at": deposit.last_checked_at.isoformat() if deposit.last_checked_at else None
        }
    else:
        return {
            "success": False,
            "deposit_id": deposit.id,
            "error": result.get('error'),
            "message": result.get('message')
        }


def _prepare_manuscript_data(manuscript: Manuscript) -> dict:
    """Prepare manuscript data for Crossref deposit."""
    return {
        'manuscript_id': manuscript.manuscript_id,
        'title': manuscript.title,
        'abstract': manuscript.abstract,
        'authors': [
            {
                'first_name': author.first_name or author.full_name.split()[0],
                'last_name': author.last_name or author.full_name.split()[-1],
                'full_name': author.full_name,
                'affiliation': author.affiliation,
                'orcid': author.orcid,
            }
            for author in manuscript.authors
        ],
        'doi': manuscript.doi,
        'published_at': manuscript.published_at.isoformat() if manuscript.published_at else None,
        'volume': manuscript.volume,
        'issue': manuscript.issue,
        'page_start': manuscript.page_start,
        'page_end': manuscript.page_end,
        'url': f"{getattr(settings, 'JOURNAL_URL', 'https://journal.example.com')}/article/{manuscript.manuscript_id}",
        'pdf_url': f"{getattr(settings, 'JOURNAL_URL', 'https://journal.example.com')}/article/{manuscript.manuscript_id}/pdf",
    }


async def _submit_to_crossref(
    deposit_id: int,
    xml_content: str,
    environment: str,
    db: Session
):
    """Background task to submit DOI to Crossref."""
    try:
        # Get credentials
        crossref_username = getattr(settings, 'CROSSREF_USERNAME', None)
        crossref_password = getattr(settings, 'CROSSREF_PASSWORD', None)

        if not crossref_username or not crossref_password:
            # Update deposit as failed
            deposit = db.query(DOIDeposit).filter(DOIDeposit.id == deposit_id).first()
            if deposit:
                deposit.status = DOIStatus.FAILED
                deposit.error_message = "Crossref credentials not configured"
                db.commit()
            return

        # Initialize API
        env = CrossrefEnvironment.PRODUCTION if environment == "production" else CrossrefEnvironment.TEST
        api_service = CrossrefAPIService(
            username=crossref_username,
            password=crossref_password,
            environment=env
        )

        # Submit
        result = await api_service.deposit_doi(xml_content)

        # Update deposit
        deposit = db.query(DOIDeposit).filter(DOIDeposit.id == deposit_id).first()
        if deposit:
            deposit.status = result['status']
            deposit.submitted_at = datetime.utcnow()

            if result['success']:
                deposit.submission_id = result.get('submission_id')
                deposit.response_message = result.get('message')
            else:
                deposit.error_message = result.get('error')

            # Log
            log = DOIDepositLog(
                deposit_id=deposit.id,
                action="submit",
                status_before=DOIStatus.PENDING.value,
                status_after=deposit.status.value,
                message=result.get('message'),
                response_data=json.dumps(result)
            )
            db.add(log)
            db.commit()

    except Exception as e:
        # Log error
        deposit = db.query(DOIDeposit).filter(DOIDeposit.id == deposit_id).first()
        if deposit:
            deposit.status = DOIStatus.FAILED
            deposit.error_message = str(e)
            db.commit()
