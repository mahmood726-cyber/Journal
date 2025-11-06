"""
Pydantic schemas for theme marketplace
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime


class ColorPalette(BaseModel):
    """Color palette definition"""
    primary: Dict[str, str]
    gray: Dict[str, str]
    success: str
    warning: str
    error: str
    info: str
    background: str
    surface: str
    text: Dict[str, str]


class Typography(BaseModel):
    """Typography definition"""
    fontFamily: Dict[str, List[str]]
    fontSize: Dict[str, str]
    lineHeight: Dict[str, float]


class ThemeBase(BaseModel):
    """Base theme fields"""
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    category: str = Field(...)
    colors: ColorPalette
    typography: Typography
    border_radius: str = Field(default="0.5rem", alias="borderRadius")

    @validator('category')
    def validate_category(cls, v):
        valid_categories = [
            'academic', 'modern', 'medical', 'nature', 'minimal',
            'humanities', 'law', 'technology', 'social', 'business', 'bold'
        ]
        if v not in valid_categories:
            raise ValueError(f'Category must be one of: {", ".join(valid_categories)}')
        return v


class ThemeCreate(ThemeBase):
    """Schema for creating a new theme"""
    author: Optional[str] = None
    version: Optional[str] = "1.0.0"
    preview_image_url: Optional[str] = None


class ThemeUpdate(BaseModel):
    """Schema for updating a theme"""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, min_length=10, max_length=500)
    category: Optional[str] = None
    colors: Optional[ColorPalette] = None
    typography: Optional[Typography] = None
    border_radius: Optional[str] = Field(None, alias="borderRadius")
    preview_image_url: Optional[str] = None


class ThemeResponse(BaseModel):
    """Schema for theme in list view"""
    id: int
    theme_id: str
    name: str
    description: str
    category: str
    author: str
    version: str
    download_count: int
    average_rating: float
    rating_count: int
    preview_image_url: Optional[str]
    is_approved: bool
    created_at: datetime

    class Config:
        orm_mode = True


class ThemeDetailResponse(ThemeResponse):
    """Schema for detailed theme view"""
    colors: Dict[str, Any]
    typography: Dict[str, Any]
    border_radius: str
    author_email: Optional[str]
    approved_at: Optional[datetime]

    @validator('colors', pre=True)
    def parse_colors(cls, v):
        if isinstance(v, str):
            import json
            return json.loads(v)
        return v

    @validator('typography', pre=True)
    def parse_typography(cls, v):
        if isinstance(v, str):
            import json
            return json.loads(v)
        return v


class ThemeRating(BaseModel):
    """Schema for rating a theme"""
    rating: int = Field(..., ge=1, le=5)
    review: Optional[str] = Field(None, max_length=1000)


class ThemeRatingResponse(BaseModel):
    """Schema for theme rating response"""
    id: int
    theme_id: int
    user_id: int
    rating: int
    review: Optional[str]
    created_at: datetime
    updated_at: datetime

    # Include user info
    user_name: Optional[str] = None
    user_avatar: Optional[str] = None

    class Config:
        orm_mode = True


class ThemeStats(BaseModel):
    """Statistics for a theme"""
    downloads: int
    average_rating: float
    rating_count: int
    five_star: int
    four_star: int
    three_star: int
    two_star: int
    one_star: int
