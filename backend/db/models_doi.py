"""
Database models for DOI management and Crossref deposits.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.base import Base
import enum


class DOIStatus(str, enum.Enum):
    """DOI registration status."""
    PENDING = "pending"
    SUBMITTED = "submitted"
    SUCCESS = "success"
    FAILED = "failed"
    WARNING = "warning"


class DOIDeposit(Base):
    """
    Track DOI deposits to Crossref.

    Each deposit represents a submission to Crossref's API.
    Can include single or multiple manuscripts.
    """
    __tablename__ = "doi_deposits"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(String(100), unique=True, index=True, nullable=False)
    submission_id = Column(String(100), index=True)

    # Manuscripts in this deposit (JSON array of manuscript IDs)
    manuscript_ids = Column(Text)  # JSON array

    # Status
    status = Column(SQLEnum(DOIStatus), default=DOIStatus.PENDING, index=True)

    # Crossref response
    response_message = Column(Text)
    error_message = Column(Text)

    # Counters
    records_total = Column(Integer, default=0)
    records_success = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    records_warning = Column(Integer, default=0)

    # XML content (stored for reference and resubmission)
    xml_content = Column(Text)

    # Depositor
    deposited_by_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    deposited_by = relationship("User", foreign_keys=[deposited_by_id])

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    submitted_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    last_checked_at = Column(DateTime(timezone=True))

    # Environment (test vs production)
    environment = Column(String(20), default="test")

    # Retry information
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)


class ManuscriptDOI(Base):
    """
    Track DOI information for individual manuscripts.

    Links manuscripts to their DOI deposits and tracks registration status.
    """
    __tablename__ = "manuscript_dois"

    id = Column(Integer, primary_key=True, index=True)
    manuscript_id = Column(Integer, ForeignKey('manuscripts.id'), unique=True, nullable=False, index=True)
    manuscript = relationship("Manuscript", back_populates="doi_record")

    # DOI information
    doi = Column(String(255), unique=True, index=True, nullable=False)
    doi_url = Column(String(500))  # Full https://doi.org/... URL

    # Registration status
    status = Column(SQLEnum(DOIStatus), default=DOIStatus.PENDING, index=True)

    # Crossref deposit reference
    deposit_id = Column(Integer, ForeignKey('doi_deposits.id'), index=True)
    deposit = relationship("DOIDeposit")

    # Registration details
    registered_at = Column(DateTime(timezone=True))
    registration_agency = Column(String(50), default="crossref")

    # Metadata
    prefix = Column(String(20))  # DOI prefix (e.g., "10.1234")
    suffix = Column(String(255))  # DOI suffix

    # Status checks
    last_verified_at = Column(DateTime(timezone=True))
    verification_status = Column(String(50))
    verification_message = Column(Text)

    # Auto-update flag
    auto_update = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DOIDepositLog(Base):
    """
    Detailed log of DOI deposit attempts and status changes.

    Provides audit trail for debugging and monitoring.
    """
    __tablename__ = "doi_deposit_logs"

    id = Column(Integer, primary_key=True, index=True)
    deposit_id = Column(Integer, ForeignKey('doi_deposits.id'), nullable=False, index=True)
    deposit = relationship("DOIDeposit")

    # Log entry
    action = Column(String(50), nullable=False, index=True)  # submit, query, update, retry
    status_before = Column(String(50))
    status_after = Column(String(50))

    # Details
    message = Column(Text)
    response_data = Column(Text)  # JSON
    error_data = Column(Text)  # JSON

    # Metadata
    performed_by_id = Column(Integer, ForeignKey('users.id'))
    performed_by = relationship("User")

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
