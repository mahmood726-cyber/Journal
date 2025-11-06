"""
Database models for the journal management system.
"""
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, ForeignKey,
    Enum as SQLEnum, Table, Float, JSON
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from .base import Base


# Enums
class UserRole(str, enum.Enum):
    """User roles in the system."""
    ADMIN = "admin"
    EDITOR_IN_CHIEF = "editor_in_chief"
    ASSOCIATE_EDITOR = "associate_editor"
    REVIEWER = "reviewer"
    AUTHOR = "author"
    READER = "reader"


class ManuscriptStatus(str, enum.Enum):
    """Manuscript workflow statuses."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    REVISIONS_REQUIRED = "revisions_required"
    REVISED = "revised"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    PUBLISHED = "published"
    WITHDRAWN = "withdrawn"


class ReviewStatus(str, enum.Enum):
    """Review statuses."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DECLINED = "declined"


class ReviewRecommendation(str, enum.Enum):
    """Review recommendations."""
    ACCEPT = "accept"
    MINOR_REVISIONS = "minor_revisions"
    MAJOR_REVISIONS = "major_revisions"
    REJECT = "reject"


class DecisionType(str, enum.Enum):
    """Editorial decision types."""
    DESK_REJECT = "desk_reject"
    SEND_FOR_REVIEW = "send_for_review"
    MINOR_REVISIONS = "minor_revisions"
    MAJOR_REVISIONS = "major_revisions"
    ACCEPT = "accept"
    REJECT = "reject"


# Association tables for many-to-many relationships
manuscript_authors = Table(
    'manuscript_authors',
    Base.metadata,
    Column('manuscript_id', Integer, ForeignKey('manuscripts.id'), primary_key=True),
    Column('author_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('author_order', Integer, nullable=False),
    Column('is_corresponding', Boolean, default=False)
)

user_specializations = Table(
    'user_specializations',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('specialization_id', Integer, ForeignKey('specializations.id'), primary_key=True)
)


# Models
class User(Base):
    """User model for all system users."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)

    # Professional information
    affiliation = Column(String(500))
    department = Column(String(255))
    country = Column(String(100))
    orcid = Column(String(19), unique=True, index=True)  # ORCID format: 0000-0000-0000-0000

    # Contact
    phone = Column(String(50))

    # Profile
    bio = Column(Text)
    website = Column(String(500))

    # Role and permissions
    role = Column(SQLEnum(UserRole), default=UserRole.AUTHOR, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))

    # Relationships
    manuscripts = relationship("Manuscript", secondary=manuscript_authors, back_populates="authors")
    submitted_manuscripts = relationship("Manuscript", back_populates="submitter")
    reviews = relationship("Review", back_populates="reviewer")
    decisions = relationship("EditorialDecision", back_populates="editor")
    specializations = relationship("Specialization", secondary=user_specializations, back_populates="users")


class Specialization(Base):
    """Subject areas/specializations for reviewers and manuscripts."""
    __tablename__ = "specializations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey('specializations.id'), nullable=True)

    # Relationships
    children = relationship("Specialization", backref="parent", remote_side=[id])
    users = relationship("User", secondary=user_specializations, back_populates="specializations")
    manuscripts = relationship("Manuscript", back_populates="specialization")


class Manuscript(Base):
    """Manuscript/article model."""
    __tablename__ = "manuscripts"

    id = Column(Integer, primary_key=True, index=True)
    manuscript_id = Column(String(50), unique=True, index=True, nullable=False)  # e.g., MS-2024-001

    # Metadata
    title = Column(String(1000), nullable=False)
    abstract = Column(Text, nullable=False)
    keywords = Column(JSON)  # List of keywords

    # Classification
    specialization_id = Column(Integer, ForeignKey('specializations.id'))
    article_type = Column(String(100))  # Research Article, Review, Case Study, etc.

    # Files
    manuscript_file = Column(String(500))  # Path to manuscript file
    supplementary_files = Column(JSON)  # List of supplementary file paths
    figures = Column(JSON)  # List of figure file paths

    # Workflow
    status = Column(SQLEnum(ManuscriptStatus), default=ManuscriptStatus.DRAFT, nullable=False)
    version = Column(Integer, default=1)
    is_resubmission = Column(Boolean, default=False)
    original_manuscript_id = Column(Integer, ForeignKey('manuscripts.id'), nullable=True)

    # Submission
    submitter_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    submitted_at = Column(DateTime(timezone=True))

    # Publication
    published_at = Column(DateTime(timezone=True))
    doi = Column(String(255), unique=True, index=True)
    volume = Column(Integer)
    issue = Column(Integer)
    page_start = Column(Integer)
    page_end = Column(Integer)

    # Files for published article
    html_file = Column(String(500))
    pdf_file = Column(String(500))
    jats_xml_file = Column(String(500))

    # Metrics
    views = Column(Integer, default=0)
    downloads = Column(Integer, default=0)

    # PubMed
    pubmed_id = Column(String(50), unique=True, index=True)
    pmc_id = Column(String(50), unique=True, index=True)
    submitted_to_pmc = Column(Boolean, default=False)
    pmc_submission_date = Column(DateTime(timezone=True))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    authors = relationship("User", secondary=manuscript_authors, back_populates="manuscripts")
    submitter = relationship("User", back_populates="submitted_manuscripts")
    specialization = relationship("Specialization", back_populates="manuscripts")
    reviews = relationship("Review", back_populates="manuscript")
    decisions = relationship("EditorialDecision", back_populates="manuscript")
    revisions = relationship("Manuscript", backref="original")
    comments = relationship("Comment", back_populates="manuscript")


class Review(Base):
    """Peer review model."""
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    manuscript_id = Column(Integer, ForeignKey('manuscripts.id'), nullable=False)
    reviewer_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Review assignment
    invited_at = Column(DateTime(timezone=True), server_default=func.now())
    due_date = Column(DateTime(timezone=True))

    # Review status
    status = Column(SQLEnum(ReviewStatus), default=ReviewStatus.PENDING, nullable=False)
    accepted_at = Column(DateTime(timezone=True))
    declined_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))

    # Review content
    recommendation = Column(SQLEnum(ReviewRecommendation))

    # Detailed scores (1-5 scale)
    score_originality = Column(Integer)
    score_methodology = Column(Integer)
    score_significance = Column(Integer)
    score_clarity = Column(Integer)

    # Comments
    comments_to_author = Column(Text)
    comments_to_editor = Column(Text)

    # Settings
    is_blind = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    manuscript = relationship("Manuscript", back_populates="reviews")
    reviewer = relationship("User", back_populates="reviews")


class EditorialDecision(Base):
    """Editorial decisions on manuscripts."""
    __tablename__ = "editorial_decisions"

    id = Column(Integer, primary_key=True, index=True)
    manuscript_id = Column(Integer, ForeignKey('manuscripts.id'), nullable=False)
    editor_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Decision
    decision = Column(SQLEnum(DecisionType), nullable=False)
    comments = Column(Text)

    # Timestamp
    decided_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    manuscript = relationship("Manuscript", back_populates="decisions")
    editor = relationship("User", back_populates="decisions")


class Comment(Base):
    """Comments and internal notes on manuscripts."""
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    manuscript_id = Column(Integer, ForeignKey('manuscripts.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    content = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)  # Internal editor notes vs. author-visible

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    manuscript = relationship("Manuscript", back_populates="comments")
    user = relationship("User")


class EmailLog(Base):
    """Log of sent emails for audit trail."""
    __tablename__ = "email_logs"

    id = Column(Integer, primary_key=True, index=True)
    recipient = Column(String(255), nullable=False)
    subject = Column(String(500), nullable=False)
    template_name = Column(String(100))
    manuscript_id = Column(Integer, ForeignKey('manuscripts.id'), nullable=True)

    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    success = Column(Boolean, default=True)
    error_message = Column(Text)


class AuditLog(Base):
    """System audit log for tracking important actions."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    action = Column(String(255), nullable=False)
    entity_type = Column(String(100))  # manuscript, user, review, etc.
    entity_id = Column(Integer)
    details = Column(JSON)
    ip_address = Column(String(45))

    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Theme(Base):
    """Theme for marketplace - custom journal themes."""
    __tablename__ = "themes"

    id = Column(Integer, primary_key=True, index=True)
    theme_id = Column(String(100), unique=True, index=True, nullable=False)  # Slug-like ID
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False, index=True)

    # Theme configuration (stored as JSON)
    colors_json = Column(Text, nullable=False)  # JSON string of color palette
    typography_json = Column(Text, nullable=False)  # JSON string of typography
    border_radius = Column(String(20), default="0.5rem")

    # Metadata
    author = Column(String(255), nullable=False)
    author_email = Column(String(255))
    version = Column(String(20), default="1.0.0")
    preview_image_url = Column(String(500))

    # Statistics
    download_count = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    rating_count = Column(Integer, default=0)

    # Approval workflow
    is_approved = Column(Boolean, default=False)
    approved_at = Column(DateTime(timezone=True))
    approved_by_id = Column(Integer, ForeignKey('users.id'))

    # Audit
    created_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    created_by = relationship("User", foreign_keys=[created_by_id])
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    ratings = relationship("ThemeRating", back_populates="theme", cascade="all, delete-orphan")


class ThemeRating(Base):
    """User ratings and reviews for themes."""
    __tablename__ = "theme_ratings"

    id = Column(Integer, primary_key=True, index=True)
    theme_id = Column(Integer, ForeignKey('themes.id'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)

    rating = Column(Integer, nullable=False)  # 1-5 stars
    review = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    theme = relationship("Theme", back_populates="ratings")
    user = relationship("User")
