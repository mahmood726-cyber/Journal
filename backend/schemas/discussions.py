"""
Pydantic schemas for Discussions API.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class DiscussionParticipant(BaseModel):
    """Participant in a discussion."""
    user_id: int
    name: Optional[str] = None
    role: Optional[str] = None

    class Config:
        from_attributes = True


class DiscussionMessageCreate(BaseModel):
    """Schema for creating a discussion message."""
    message: str = Field(..., min_length=1, max_length=10000)
    file_ids: Optional[List[int]] = None


class DiscussionMessageResponse(BaseModel):
    """Schema for discussion message responses."""
    id: int
    discussion_id: int
    user_id: int
    user_name: str
    user_role: Optional[str] = None
    message: str
    attachments: List[dict] = []
    created_at: datetime

    class Config:
        from_attributes = True


class DiscussionCreate(BaseModel):
    """Schema for creating a discussion."""
    manuscript_id: int
    stage: str = Field(..., pattern="^(submission|review|copyediting|production)$")
    subject: str = Field(..., min_length=3, max_length=500)
    message: str = Field(..., min_length=1, max_length=10000)
    participant_ids: List[int] = Field(..., min_items=1)
    file_ids: Optional[List[int]] = None


class DiscussionUpdate(BaseModel):
    """Schema for updating a discussion."""
    subject: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = Field(None, pattern="^(active|closed)$")


class DiscussionResponse(BaseModel):
    """Schema for discussion responses."""
    id: int
    manuscript_id: int
    manuscript_title: Optional[str] = None
    stage: str
    subject: str
    created_by_id: int
    created_by_name: str
    status: str
    message_count: int
    last_message_at: Optional[datetime] = None
    created_at: datetime
    participants: List[DiscussionParticipant] = []

    class Config:
        from_attributes = True


class DiscussionDetail(DiscussionResponse):
    """Detailed discussion with all messages."""
    messages: List[DiscussionMessageResponse] = []


class DiscussionList(BaseModel):
    """Paginated list of discussions."""
    total: int
    discussions: List[DiscussionResponse]
    page: int
    page_size: int


class AddParticipantsRequest(BaseModel):
    """Request to add participants to discussion."""
    user_ids: List[int] = Field(..., min_items=1)
