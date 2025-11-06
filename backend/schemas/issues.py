"""
Pydantic schemas for Issue Management API.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime


class IssueBase(BaseModel):
    """Base issue schema."""
    volume: int = Field(..., ge=1)
    number: int = Field(..., ge=1)
    year: int = Field(..., ge=1900, le=2100)
    title: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None


class IssueCreate(IssueBase):
    """Schema for creating an issue."""
    cover_image_url: Optional[str] = None
    scheduled_publication: Optional[datetime] = None

    @validator('scheduled_publication')
    def scheduled_must_be_future(cls, v):
        if v and v < datetime.now():
            raise ValueError('Scheduled publication must be in the future')
        return v


class IssueUpdate(BaseModel):
    """Schema for updating an issue."""
    title: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    cover_image_url: Optional[str] = None
    scheduled_publication: Optional[datetime] = None


class IssueResponse(IssueBase):
    """Schema for issue responses."""
    id: int
    cover_image_url: Optional[str] = None
    is_published: bool
    published_at: Optional[datetime] = None
    scheduled_publication: Optional[datetime] = None
    doi: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    # Enriched data
    article_count: Optional[int] = 0

    class Config:
        from_attributes = True


class IssueList(BaseModel):
    """Paginated list of issues."""
    total: int
    issues: List[IssueResponse]
    page: int
    page_size: int


class ArticleInIssue(BaseModel):
    """Article information for table of contents."""
    id: int
    manuscript_id: str
    title: str
    authors: List[str]
    page_start: Optional[int] = None
    page_end: Optional[int] = None
    doi: Optional[str] = None
    article_order: int
    article_type: str
    published_at: datetime

    class Config:
        from_attributes = True


class IssueTableOfContents(BaseModel):
    """Complete table of contents for an issue."""
    issue: IssueResponse
    articles: List[ArticleInIssue]


class AddArticleToIssue(BaseModel):
    """Schema for adding article to issue."""
    manuscript_id: int
    page_start: Optional[int] = None
    page_end: Optional[int] = None


class ReorderArticles(BaseModel):
    """Schema for reordering articles in issue."""
    article_orders: List[dict] = Field(..., description="List of {manuscript_id: int, order: int}")

    @validator('article_orders')
    def validate_orders(cls, v):
        if not v:
            raise ValueError('Must provide at least one article order')

        # Check for duplicate manuscript IDs
        manuscript_ids = [item['manuscript_id'] for item in v]
        if len(manuscript_ids) != len(set(manuscript_ids)):
            raise ValueError('Duplicate manuscript IDs found')

        # Check for duplicate orders
        orders = [item['order'] for item in v]
        if len(orders) != len(set(orders)):
            raise ValueError('Duplicate order values found')

        return v


class IssuePublishRequest(BaseModel):
    """Request to publish an issue."""
    publish_date: Optional[datetime] = None
    assign_dois: bool = True
    send_notifications: bool = True


class IssueStatistics(BaseModel):
    """Statistics for issue management."""
    total_issues: int
    published_issues: int
    scheduled_issues: int
    current_year_issues: int
    articles_in_current_issue: int
    unpublished_accepted_articles: int
