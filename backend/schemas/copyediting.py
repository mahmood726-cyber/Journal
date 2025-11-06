"""
Pydantic schemas for Copyediting API.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class CopyeditingAssignmentBase(BaseModel):
    """Base copyediting assignment schema."""
    manuscript_id: int
    notes: Optional[str] = Field(None, max_length=2000)
    due_date: Optional[datetime] = None


class CopyeditingAssignmentCreate(CopyeditingAssignmentBase):
    """Schema for creating a copyediting assignment."""
    copyeditor_id: int

    @validator('due_date')
    def due_date_must_be_future(cls, v):
        if v and v < datetime.now():
            raise ValueError('Due date must be in the future')
        return v


class CopyeditingAssignmentUpdate(BaseModel):
    """Schema for updating copyediting assignment."""
    notes: Optional[str] = Field(None, max_length=2000)
    internal_notes: Optional[str] = Field(None, max_length=2000)
    due_date: Optional[datetime] = None
    status: Optional[str] = None


class CopyeditingFileUpload(BaseModel):
    """Schema for uploading copyedited file."""
    notes: Optional[str] = Field(None, max_length=1000)


class AuthorReviewRequest(BaseModel):
    """Schema for requesting author review."""
    notes_to_author: str = Field(..., min_length=10, max_length=2000)


class AuthorReviewResponse(BaseModel):
    """Schema for author's review response."""
    approved: bool
    notes: Optional[str] = Field(None, max_length=2000)
    requested_changes: Optional[str] = Field(None, max_length=2000)


class CopyeditingAssignmentResponse(CopyeditingAssignmentBase):
    """Schema for copyediting assignment responses."""
    id: int
    copyeditor_id: int
    assigned_by_id: int
    status: str
    original_file_id: Optional[int] = None
    copyedited_file_id: Optional[int] = None
    internal_notes: Optional[str] = None
    author_approved: bool
    author_notes: Optional[str] = None
    assigned_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    author_reviewed_at: Optional[datetime] = None

    # Nested relationships (optional, for detailed responses)
    copyeditor_name: Optional[str] = None
    manuscript_title: Optional[str] = None

    class Config:
        from_attributes = True


class CopyeditingStatistics(BaseModel):
    """Statistics for copyediting workflow."""
    total_assignments: int
    pending_assignments: int
    in_progress_assignments: int
    completed_assignments: int
    awaiting_author_review: int
    average_completion_days: Optional[float] = None
    overdue_assignments: int


class CopyeditingAssignmentList(BaseModel):
    """Paginated list of copyediting assignments."""
    total: int
    assignments: list[CopyeditingAssignmentResponse]
    page: int
    page_size: int
