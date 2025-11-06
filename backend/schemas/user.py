"""
Pydantic schemas for User API.
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from db.models import UserRole


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=255)
    affiliation: Optional[str] = None
    department: Optional[str] = None
    country: Optional[str] = None
    orcid: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    website: Optional[str] = None

    @validator('orcid')
    def validate_orcid(cls, v):
        if v and not v.replace('-', '').isdigit():
            raise ValueError('Invalid ORCID format')
        return v


class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str = Field(..., min_length=8, max_length=100)
    role: UserRole = UserRole.AUTHOR


class UserUpdate(BaseModel):
    """Schema for updating a user."""
    full_name: Optional[str] = None
    affiliation: Optional[str] = None
    department: Optional[str] = None
    country: Optional[str] = None
    orcid: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    website: Optional[str] = None


class UserResponse(UserBase):
    """Schema for user responses."""
    id: int
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for authentication token."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Schema for token payload."""
    sub: int
    exp: datetime
    type: str
