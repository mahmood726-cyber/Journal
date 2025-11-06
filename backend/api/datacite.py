"""
API endpoints for DataCite DOI registration.
Alternative DOI provider to Crossref.
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from datetime import datetime

from db.database import get_db
from db.models import User, Manuscript, UserRole, ManuscriptStatus
from db.models_doi import ManuscriptDOI, DOIDeposit, DOIStatus, DOIDepositLog
from api.auth import get_current_user
from services.datacite_service import get_datacite_service, DataCiteResponse
from core.config import settings


router = APIRouter()


# ============================================================================
# DataCite DOI Registration Endpoints
# ============================================================================

class RegisterDataCiteDOIRequest(BaseModel):
    """Request to register DOI with DataCite."""
    doi: Optional[str] = None  # If None, will auto-generate
    auto_assign: bool = False
    environment: str = "test"  # test or production
    state: str = "findable"  # draft, registered, findable


class RegisterDataCiteDOIResponse(BaseModel):
    """Response from DOI registration."""
    success: bool
    message: str
    doi: str
    doi_url: str
    state: str
    environment: str
    created_at: datetime


@router.post("/manuscripts/{manuscript_id}/register", response_model=RegisterDataCiteDOIResponse)
async def register_datacite_doi(
    manuscript_id: int,
    request: RegisterDataCiteDOIRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Register DOI for a manuscript with DataCite.

    DataCite is an alternative DOI provider to Crossref, commonly used
    for research data, software, and other scholarly outputs.

    Features:
    - JSON-based API (simpler than Crossref XML)
    - Supports draft DOIs (test before publishing)
    - Rich metadata support
    - Test environment available

    Permissions:
    - Editors and Admins only

    Args:
        manuscript_id: ID of manuscript to register
        request: Registration request with options
    """
    # Permission check
    if current_user.role not in [UserRole.EDITOR, UserRole.EDITOR_IN_CHIEF, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only editors can register DOIs"
        )

    # Get manuscript
    manuscript = db.query(Manuscript).filter(
        Manuscript.id == manuscript_id
    ).first()

    if not manuscript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manuscript not found"
        )

    # Check manuscript is published
    if manuscript.status != ManuscriptStatus.PUBLISHED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only published manuscripts can have DOIs registered"
        )

    # Get or assign DOI
    doi = request.doi

    if not doi and request.auto_assign:
        # Auto-generate DOI
        doi_prefix = getattr(settings, 'DATACITE_DOI_PREFIX', settings.DOI_PREFIX)
        doi = f"{doi_prefix}/{manuscript.manuscript_id}"
    elif not doi and manuscript.doi:
        # Use existing DOI
        doi = manuscript.doi
    elif not doi:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="DOI must be provided or auto_assign must be true"
        )

    # Update manuscript DOI if not already set
    if not manuscript.doi:
        manuscript.doi = doi
        db.commit()

    # Build URL
    article_url = f"{settings.JOURNAL_URL}/articles/{manuscript.manuscript_id}"

    # Get DataCite credentials
    repository_id = getattr(settings, 'DATACITE_REPOSITORY_ID', None)
    password = getattr(settings, 'DATACITE_PASSWORD', None)

    if not repository_id or not password:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="DataCite credentials not configured"
        )

    # Register with DataCite
    try:
        datacite_service = get_datacite_service(
            repository_id=repository_id,
            password=password,
            test_mode=(request.environment == "test")
        )

        response = await datacite_service.register_doi(
            doi=doi,
            manuscript=manuscript,
            url=article_url,
            state=request.state
        )

        # Create/update ManuscriptDOI record
        doi_record = db.query(ManuscriptDOI).filter(
            ManuscriptDOI.manuscript_id == manuscript_id
        ).first()

        if not doi_record:
            doi_record = ManuscriptDOI(
                manuscript_id=manuscript_id,
                doi=doi,
                doi_url=f"https://doi.org/{doi}",
                status=DOIStatus.SUCCESS
            )
            db.add(doi_record)
        else:
            doi_record.doi = doi
            doi_record.doi_url = f"https://doi.org/{doi}"
            doi_record.status = DOIStatus.SUCCESS

        doi_record.registered_at = datetime.utcnow()
        db.commit()

        return RegisterDataCiteDOIResponse(
            success=True,
            message=f"DOI successfully registered with DataCite",
            doi=response.doi,
            doi_url=response.url,
            state=response.state,
            environment=request.environment,
            created_at=response.created
        )

    except Exception as e:
        # Log error
        print(f"DataCite registration error: {str(e)}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"DataCite registration failed: {str(e)}"
        )


@router.put("/manuscripts/{manuscript_id}/update")
async def update_datacite_doi(
    manuscript_id: int,
    environment: str = "test",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update DOI metadata in DataCite.

    Use this to update metadata after the DOI is registered.

    Permissions:
    - Editors and Admins only
    """
    # Permission check
    if current_user.role not in [UserRole.EDITOR, UserRole.EDITOR_IN_CHIEF, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only editors can update DOIs"
        )

    # Get manuscript
    manuscript = db.query(Manuscript).filter(
        Manuscript.id == manuscript_id
    ).first()

    if not manuscript or not manuscript.doi:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manuscript or DOI not found"
        )

    # Get credentials
    repository_id = getattr(settings, 'DATACITE_REPOSITORY_ID', None)
    password = getattr(settings, 'DATACITE_PASSWORD', None)

    if not repository_id or not password:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="DataCite credentials not configured"
        )

    # Build URL
    article_url = f"{settings.JOURNAL_URL}/articles/{manuscript.manuscript_id}"

    # Update with DataCite
    try:
        datacite_service = get_datacite_service(
            repository_id=repository_id,
            password=password,
            test_mode=(environment == "test")
        )

        response = await datacite_service.update_doi(
            doi=manuscript.doi,
            manuscript=manuscript,
            url=article_url
        )

        return {
            "success": True,
            "message": "DOI metadata updated successfully",
            "doi": response.doi,
            "updated_at": response.updated
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"DataCite update failed: {str(e)}"
        )


@router.get("/manuscripts/{manuscript_id}/status")
async def get_datacite_doi_status(
    manuscript_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get DOI status from DataCite.

    Permissions:
    - Editors and authors
    """
    # Get manuscript
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
            "message": "No DOI registration record found"
        }

    return {
        "manuscript_id": manuscript_id,
        "doi": doi_record.doi,
        "doi_url": doi_record.doi_url,
        "registered": True,
        "status": doi_record.status,
        "registered_at": doi_record.registered_at
    }


# ============================================================================
# DataCite vs Crossref Comparison Endpoint
# ============================================================================

@router.get("/doi-providers/compare")
async def compare_doi_providers(
    current_user: User = Depends(get_current_user)
):
    """
    Compare DataCite and Crossref as DOI providers.

    Helps editors choose the right provider for their needs.

    Permissions:
    - Editors and Admins only
    """
    if current_user.role not in [UserRole.EDITOR, UserRole.EDITOR_IN_CHIEF, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Editor access required"
        )

    comparison = {
        "crossref": {
            "name": "Crossref",
            "best_for": [
                "Journal articles",
                "Books and chapters",
                "Conference proceedings",
                "Traditional scholarly publishing"
            ],
            "metadata_format": "XML (Crossref Schema 5.3.1)",
            "api_complexity": "High (XML-based)",
            "citation_tracking": "Excellent (Crossref Event Data)",
            "cost": "Per-DOI fee ($1 for open access)",
            "features": [
                "Similarity Check (Crossref Similarity Check)",
                "Metadata search API",
                "Funding data tracking",
                "Clinical trials registration"
            ]
        },
        "datacite": {
            "name": "DataCite",
            "best_for": [
                "Research data",
                "Software",
                "Datasets",
                "Gray literature",
                "Preprints",
                "Alternative outputs"
            ],
            "metadata_format": "JSON (DataCite Metadata Schema 4.4)",
            "api_complexity": "Low (REST JSON)",
            "citation_tracking": "Good (DataCite Event Data)",
            "cost": "Annual membership fee (no per-DOI cost)",
            "features": [
                "Draft DOIs (test before publishing)",
                "Rich relatedIdentifier support",
                "GeoLocation support",
                "Version tracking"
            ]
        },
        "recommendation": {
            "for_journals": "Crossref is the industry standard for journal articles",
            "for_data": "DataCite is better for datasets and research outputs",
            "for_both": "Use both - Crossref for articles, DataCite for supplementary data",
            "cost_comparison": "DataCite may be cheaper for high-volume publishers"
        }
    }

    return comparison
