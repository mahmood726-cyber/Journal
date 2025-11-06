"""
API endpoints for AI-powered features using local Llama.
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from db.database import get_db
from db.models import User, Manuscript, UserRole
from api.auth import get_current_user
from services.plagiarism_service import get_plagiarism_service, PlagiarismReport
from services.llm_service import get_llm_service


router = APIRouter()


# ============================================================================
# Plagiarism Detection Endpoints
# ============================================================================

class PlagiarismCheckRequest(BaseModel):
    """Request to check manuscript for plagiarism."""
    manuscript_id: int


class PlagiarismCheckResponse(BaseModel):
    """Response from plagiarism check."""
    success: bool
    message: str
    report: Optional[PlagiarismReport] = None
    job_id: Optional[str] = None


@router.post("/plagiarism/check", response_model=PlagiarismCheckResponse)
async def check_manuscript_plagiarism(
    request: PlagiarismCheckRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check manuscript for plagiarism using local LLM.

    This replaces paid services like iThenticate/Turnitin with zero-cost
    local AI-powered plagiarism detection.

    Features:
    - Semantic similarity detection
    - Internal corpus checking
    - Self-plagiarism detection
    - AI-powered match analysis

    Permissions:
    - Editors and Admins can check any manuscript
    - Authors can check their own manuscripts
    """
    # Get manuscript
    manuscript = db.query(Manuscript).filter(
        Manuscript.id == request.manuscript_id
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
            detail="Not authorized to check this manuscript"
        )

    # Get manuscript text
    manuscript_text = f"{manuscript.title}\n\n{manuscript.abstract}"

    # Note: In production, you'd want to extract full text from manuscript file
    # For now, using title + abstract as a proof of concept

    if len(manuscript_text) < 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Manuscript text too short for plagiarism check"
        )

    # Get author IDs for self-plagiarism detection
    author_ids = [author.id for author in manuscript.authors]

    # Run plagiarism check
    try:
        plagiarism_service = get_plagiarism_service()
        report = await plagiarism_service.check_plagiarism(
            manuscript_id=manuscript.id,
            manuscript_text=manuscript_text,
            title=manuscript.title,
            author_ids=author_ids,
            db=db
        )

        return PlagiarismCheckResponse(
            success=True,
            message=f"Plagiarism check complete. Found {len(report.matches)} potential matches.",
            report=report
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Plagiarism check failed: {str(e)}"
        )


@router.get("/plagiarism/report/{manuscript_id}", response_model=PlagiarismReport)
async def get_plagiarism_report(
    manuscript_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get existing plagiarism report for a manuscript.

    Note: In production, you'd store reports in the database.
    This is a placeholder that returns a new check.
    """
    # Permission check
    manuscript = db.query(Manuscript).filter(Manuscript.id == manuscript_id).first()

    if not manuscript:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manuscript not found"
        )

    is_author = any(author.id == current_user.id for author in manuscript.authors)
    is_editor = current_user.role in [UserRole.EDITOR, UserRole.EDITOR_IN_CHIEF, UserRole.ADMIN]

    if not (is_author or is_editor):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this report"
        )

    # In production: query database for stored report
    # For now: return new check
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No stored report found. Run a new plagiarism check."
    )


# ============================================================================
# LLM Health & Status Endpoints
# ============================================================================

class LLMHealthResponse(BaseModel):
    """LLM service health status."""
    status: str
    ollama_available: bool
    models: List[str]
    message: str


@router.get("/llm/health", response_model=LLMHealthResponse)
async def check_llm_health(
    current_user: User = Depends(get_current_user)
):
    """
    Check health of local LLM service (Ollama).

    Only available to admins for monitoring.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    llm_service = get_llm_service()

    try:
        # Check if Ollama is running
        is_healthy = await llm_service.health_check()

        if not is_healthy:
            return LLMHealthResponse(
                status="unhealthy",
                ollama_available=False,
                models=[],
                message="Ollama service is not responding. Check if it's running."
            )

        # Get available models
        models_list = await llm_service.list_models()
        model_names = [m['name'] for m in models_list]

        return LLMHealthResponse(
            status="healthy",
            ollama_available=True,
            models=model_names,
            message=f"Ollama is running with {len(model_names)} models available."
        )

    except Exception as e:
        return LLMHealthResponse(
            status="error",
            ollama_available=False,
            models=[],
            message=f"Error checking LLM service: {str(e)}"
        )


class TestGenerationRequest(BaseModel):
    """Request for test text generation."""
    prompt: str
    temperature: float = 0.7
    max_tokens: Optional[int] = 100


class TestGenerationResponse(BaseModel):
    """Response from test generation."""
    text: str
    model: str
    tokens_used: int


@router.post("/llm/test-generation", response_model=TestGenerationResponse)
async def test_llm_generation(
    request: TestGenerationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Test LLM text generation.

    Only available to admins for testing.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    llm_service = get_llm_service()

    try:
        response = await llm_service.generate(
            prompt=request.prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        return TestGenerationResponse(
            text=response.text,
            model=response.model,
            tokens_used=response.tokens_used
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generation failed: {str(e)}"
        )


# ============================================================================
# Reviewer Matching Endpoints (Coming Soon)
# ============================================================================

@router.get("/reviewer-matching/suggest/{manuscript_id}")
async def suggest_reviewers(
    manuscript_id: int,
    num_reviewers: int = 5,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Suggest best reviewers for a manuscript using AI matching.

    Coming soon in Phase 2.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="AI reviewer matching coming soon"
    )


# ============================================================================
# Email Template Generation Endpoints (Coming Soon)
# ============================================================================

@router.post("/email-templates/generate")
async def generate_email_template(
    current_user: User = Depends(get_current_user)
):
    """
    Generate personalized email template using AI.

    Coming soon in Phase 2.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="AI email template generation coming soon"
    )
