"""
Pydantic schemas for Production API.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class ProductionAssignmentBase(BaseModel):
    """Base production assignment schema."""
    manuscript_id: int
    assigned_to_id: int
    task_type: str = Field(..., pattern="^(layout|proofreading|galley_conversion)$")
    due_date: Optional[datetime] = None


class ProductionAssignmentCreate(ProductionAssignmentBase):
    """Schema for creating a production assignment."""
    galley_format: Optional[str] = Field(None, pattern="^(pdf|html|xml|epub)$")
    galley_label: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=2000)

    @validator('due_date')
    def due_date_must_be_future(cls, v):
        if v and v < datetime.now():
            raise ValueError('Due date must be in the future')
        return v


class ProductionAssignmentUpdate(BaseModel):
    """Schema for updating production assignment."""
    status: Optional[str] = None
    due_date: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=2000)


class GalleyGenerationRequest(BaseModel):
    """Request for automated galley generation."""
    format: str = Field(..., pattern="^(pdf|html|xml|epub)$")
    label: Optional[str] = Field(None, max_length=100)
    include_metadata: bool = True
    include_references: bool = True


class GalleyResponse(BaseModel):
    """Response for galley generation/upload."""
    id: int
    manuscript_id: int
    format: str
    label: str
    file_path: str
    file_size: int
    generated_at: datetime
    version: int

    class Config:
        from_attributes = True


class ProductionAssignmentResponse(ProductionAssignmentBase):
    """Schema for production assignment responses."""
    id: int
    assigned_by_id: int
    task_type: str
    galley_format: Optional[str] = None
    galley_label: Optional[str] = None
    source_file_id: Optional[int] = None
    output_file_id: Optional[int] = None
    status: str
    notes: Optional[str] = None
    assigned_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Enriched data
    assigned_to_name: Optional[str] = None
    manuscript_title: Optional[str] = None

    class Config:
        from_attributes = True


class ProductionStatistics(BaseModel):
    """Statistics for production workflow."""
    total_assignments: int
    pending_assignments: int
    in_progress_assignments: int
    completed_assignments: int
    layout_assignments: int
    proofreading_assignments: int
    galley_assignments: int
    overdue_assignments: int
    average_completion_days: Optional[float] = None


class ProductionAssignmentList(BaseModel):
    """Paginated list of production assignments."""
    total: int
    assignments: List[ProductionAssignmentResponse]
    page: int
    page_size: int


class ManuscriptGalleyList(BaseModel):
    """List of galleys for a manuscript."""
    manuscript_id: int
    manuscript_title: str
    galleys: List[GalleyResponse]
