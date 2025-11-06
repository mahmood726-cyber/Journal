"""
Database models for COUNTER R5 compliant article metrics.
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from .base import Base


class EventType(str, enum.Enum):
    """COUNTER R5 event types."""
    # Item Requests
    ABSTRACT_VIEW = "abstract_view"
    FULL_TEXT_VIEW = "full_text_view"
    PDF_DOWNLOAD = "pdf_download"
    XML_DOWNLOAD = "xml_download"
    HTML_VIEW = "html_view"

    # Item Investigations
    LANDING_PAGE_VIEW = "landing_page_view"
    TOC_VIEW = "toc_view"

    # Other events
    CITATION_EXPORT = "citation_export"
    SUPPLEMENTARY_DOWNLOAD = "supplementary_download"


class ArticleMetricEvent(Base):
    """
    Individual metric events for COUNTER R5 compliance.

    Tracks every view, download, and interaction with articles.
    Follows COUNTER Code of Practice Release 5 specifications.
    """
    __tablename__ = "article_metric_events"

    id = Column(Integer, primary_key=True, index=True)

    # Article reference
    manuscript_id = Column(Integer, ForeignKey('manuscripts.id'), nullable=False, index=True)

    # Event details
    event_type = Column(String(50), nullable=False, index=True)
    event_date = Column(Date, nullable=False, index=True)
    event_timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # User information (anonymous tracking allowed)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    session_id = Column(String(100), index=True)
    ip_address = Column(String(45))  # IPv4 or IPv6
    user_agent = Column(Text)

    # Geographic information
    country_code = Column(String(2), index=True)  # ISO 3166-1 alpha-2
    city = Column(String(100))
    region = Column(String(100))

    # Referrer information
    referrer = Column(Text)
    referrer_category = Column(String(50))  # search_engine, social_media, direct, other

    # COUNTER R5 compliance flags
    is_robot = Column(Boolean, default=False)  # Filtered out for COUNTER reports
    is_unique = Column(Boolean, default=True)  # First event of this type for this session/date

    # Double-click filter (COUNTER requirement)
    is_double_click = Column(Boolean, default=False)

    # Relationships
    manuscript = relationship("Manuscript", foreign_keys=[manuscript_id])
    user = relationship("User", foreign_keys=[user_id])


class ArticleMetricSummary(Base):
    """
    Aggregated article metrics by day for performance.

    Pre-computed daily summaries for faster reporting.
    """
    __tablename__ = "article_metric_summaries"

    id = Column(Integer, primary_key=True, index=True)
    manuscript_id = Column(Integer, ForeignKey('manuscripts.id'), nullable=False, index=True)
    metric_date = Column(Date, nullable=False, index=True)

    # COUNTER R5 metrics
    total_item_requests = Column(Integer, default=0)  # All downloads
    unique_item_requests = Column(Integer, default=0)  # Unique downloads
    total_item_investigations = Column(Integer, default=0)  # All views
    unique_item_investigations = Column(Integer, default=0)  # Unique views

    # Breakdown by type
    abstract_views = Column(Integer, default=0)
    full_text_views = Column(Integer, default=0)
    pdf_downloads = Column(Integer, default=0)
    xml_downloads = Column(Integer, default=0)
    html_views = Column(Integer, default=0)

    # Geographic breakdown (top countries)
    top_countries = Column(Text)  # JSON: {"US": 45, "UK": 23, ...}

    # Referrer breakdown
    referrer_breakdown = Column(Text)  # JSON: {"search": 40, "social": 30, ...}

    # Last updated
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    manuscript = relationship("Manuscript", foreign_keys=[manuscript_id])


class JournalMetricSummary(Base):
    """
    Journal-wide metrics aggregated by month.

    For COUNTER reporting and journal-level analytics.
    """
    __tablename__ = "journal_metric_summaries"

    id = Column(Integer, primary_key=True, index=True)

    # Time period
    year = Column(Integer, nullable=False, index=True)
    month = Column(Integer, nullable=False, index=True)

    # COUNTER R5 journal-level metrics
    total_item_requests = Column(Integer, default=0)
    unique_item_requests = Column(Integer, default=0)
    total_item_investigations = Column(Integer, default=0)
    unique_item_investigations = Column(Integer, default=0)

    # Article counts
    articles_published = Column(Integer, default=0)
    articles_with_activity = Column(Integer, default=0)

    # Top articles (JSON)
    top_articles = Column(Text)  # JSON: [{"id": 1, "title": "...", "views": 500}, ...]

    # Geographic distribution
    countries_reached = Column(Integer, default=0)
    top_countries = Column(Text)  # JSON

    # Created/updated
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ArticleAltmetrics(Base):
    """
    Alternative metrics (Altmetrics) for articles.

    Tracks social media mentions, citations, etc.
    """
    __tablename__ = "article_altmetrics"

    id = Column(Integer, primary_key=True, index=True)
    manuscript_id = Column(Integer, ForeignKey('manuscripts.id'), unique=True, nullable=False)

    # Citation metrics
    crossref_citations = Column(Integer, default=0)
    scopus_citations = Column(Integer, default=0)
    google_scholar_citations = Column(Integer, default=0)

    # Social media metrics
    twitter_mentions = Column(Integer, default=0)
    facebook_shares = Column(Integer, default=0)
    linkedin_shares = Column(Integer, default=0)
    reddit_mentions = Column(Integer, default=0)

    # Academic platforms
    mendeley_readers = Column(Integer, default=0)
    researchgate_reads = Column(Integer, default=0)

    # Media coverage
    news_mentions = Column(Integer, default=0)
    blog_mentions = Column(Integer, default=0)

    # Altmetric score (if using Altmetric.com API)
    altmetric_score = Column(Integer, default=0)

    # Last updated
    last_updated = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    manuscript = relationship("Manuscript", foreign_keys=[manuscript_id])
