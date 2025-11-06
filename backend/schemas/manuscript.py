"""
Pydantic schemas for Manuscript API.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from db.models import ManuscriptStatus


class AuthorInfo(BaseModel):
    """Author information for manuscript."""
    user_id: int
    order: int
    is_corresponding: bool = False


class ManuscriptBase(BaseModel):
    """Base manuscript schema."""
    title: str = Field(..., min_length=10, max_length=1000)
    abstract: str = Field(..., min_length=50)
    keywords: List[str] = Field(..., min_items=3, max_items=10)
    specialization_id: int
    article_type: str


class ManuscriptCreate(ManuscriptBase):
    """Schema for creating a manuscript."""
    authors: List[AuthorInfo] = Field(..., min_items=1)


class ManuscriptUpdate(BaseModel):
    """Schema for updating a manuscript."""
    title: Optional[str] = None
    abstract: Optional[str] = None
    keywords: Optional[List[str]] = None
    specialization_id: Optional[int] = None
    article_type: Optional[str] = None


class ManuscriptResponse(ManuscriptBase):
    """Schema for manuscript responses."""
    id: int
    manuscript_id: str
    status: ManuscriptStatus
    version: int
    submitter_id: int
    submitted_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    doi: Optional[str] = None
    volume: Optional[int] = None
    issue: Optional[int] = None
    views: int
    downloads: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ManuscriptSubmit(BaseModel):
    """Schema for submitting a manuscript."""
    manuscript_id: int


class ManuscriptPublish(BaseModel):
    """Schema for publishing a manuscript."""
    volume: int
    issue: int
    page_start: Optional[int] = None
    page_end: Optional[int] = None
