"""
Multi-Journal Management Platform

Allows managing multiple journals from a single installation.
Enterprise feature for publishers with multiple journal brands.
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MultiJournalManager:
    """
    Manage multiple journals within one platform.

    Features:
    - Separate journal configurations
    - Shared user pool with journal-specific roles
    - Cross-journal analytics
    - Centralized billing (for hybrid OA)
    - White-label customization per journal
    """

    def __init__(self, db_session: Session):
        self.db = db_session

    def create_journal(
        self,
        title: str,
        short_title: str,
        issn: str,
        eissn: str,
        publisher_name: str,
        description: str,
        subject_areas: List[str],
        website_url: str,
        email: str,
        editor_in_chief_id: int,
        branding: Optional[Dict] = None
    ) -> 'Journal':
        """
        Create a new journal in the platform.

        Args:
            title: Full journal title
            short_title: Abbreviated title
            issn: Print ISSN
            eissn: Electronic ISSN
            publisher_name: Publisher name
            description: Journal description
            subject_areas: List of subject areas
            website_url: Journal website URL
            email: Contact email
            editor_in_chief_id: User ID of editor-in-chief
            branding: Custom branding configuration

        Returns:
            Journal object
        """
        from db.models import Journal, User, UserRole

        # Verify editor exists
        editor = self.db.query(User).filter(User.id == editor_in_chief_id).first()
        if not editor:
            raise ValueError(f"User {editor_in_chief_id} not found")

        # Ensure editor has appropriate role
        if editor.role not in [UserRole.EDITOR_IN_CHIEF, UserRole.ADMIN]:
            raise ValueError("User must have editor or admin role")

        # Create journal
        new_journal = Journal(
            title=title,
            short_title=short_title,
            issn=issn,
            eissn=eissn,
            publisher_name=publisher_name,
            description=description,
            subject_areas=subject_areas,
            website_url=website_url,
            email=email,
            editor_in_chief_id=editor_in_chief_id,
            branding=branding or {},
            is_active=True,
            created_at=datetime.utcnow()
        )

        self.db.add(new_journal)
        self.db.commit()
        self.db.refresh(new_journal)

        logger.info(f"Created journal: {title} (ID: {new_journal.id})")

        return new_journal

    def get_journal(self, journal_id: int) -> Optional['Journal']:
        """Get journal by ID."""
        from db.models import Journal

        return self.db.query(Journal).filter(Journal.id == journal_id).first()

    def list_journals(
        self,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> List['Journal']:
        """List all journals in the platform."""
        from db.models import Journal

        query = self.db.query(Journal)

        if active_only:
            query = query.filter(Journal.is_active == True)

        return query.offset(skip).limit(limit).all()

    def update_journal(
        self,
        journal_id: int,
        updates: Dict
    ) -> 'Journal':
        """Update journal configuration."""
        from db.models import Journal

        journal = self.get_journal(journal_id)
        if not journal:
            raise ValueError(f"Journal {journal_id} not found")

        # Update fields
        for key, value in updates.items():
            if hasattr(journal, key):
                setattr(journal, key, value)

        journal.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(journal)

        return journal

    def deactivate_journal(self, journal_id: int) -> None:
        """Deactivate a journal (soft delete)."""
        journal = self.get_journal(journal_id)
        if journal:
            journal.is_active = False
            journal.deactivated_at = datetime.utcnow()
            self.db.commit()

    def get_journal_statistics(self, journal_id: int) -> Dict:
        """Get comprehensive statistics for a journal."""
        from db.models import Manuscript, Review, User

        journal = self.get_journal(journal_id)
        if not journal:
            return {}

        # Manuscript statistics
        total_manuscripts = self.db.query(Manuscript).filter(
            Manuscript.journal_id == journal_id
        ).count()

        published = self.db.query(Manuscript).filter(
            Manuscript.journal_id == journal_id,
            Manuscript.status == 'published'
        ).count()

        # Review statistics
        manuscripts_with_reviews = self.db.query(Manuscript).filter(
            Manuscript.journal_id == journal_id
        ).all()

        manuscript_ids = [m.id for m in manuscripts_with_reviews]

        total_reviews = self.db.query(Review).filter(
            Review.manuscript_id.in_(manuscript_ids)
        ).count() if manuscript_ids else 0

        # Impact metrics
        total_views = self.db.query(func.sum(Manuscript.views)).filter(
            Manuscript.journal_id == journal_id
        ).scalar() or 0

        total_downloads = self.db.query(func.sum(Manuscript.downloads)).filter(
            Manuscript.journal_id == journal_id
        ).scalar() or 0

        return {
            'journal_id': journal_id,
            'title': journal.title,
            'total_manuscripts': total_manuscripts,
            'published_articles': published,
            'total_reviews': total_reviews,
            'total_views': total_views,
            'total_downloads': total_downloads,
            'avg_views_per_article': total_views / published if published > 0 else 0,
            'avg_downloads_per_article': total_downloads / published if published > 0 else 0
        }

    def assign_user_to_journal(
        self,
        user_id: int,
        journal_id: int,
        role: str
    ) -> None:
        """
        Assign a user to a specific journal with a role.
        Users can have different roles in different journals.
        """
        from db.models import JournalUserRole

        # Check if assignment already exists
        existing = self.db.query(JournalUserRole).filter(
            JournalUserRole.user_id == user_id,
            JournalUserRole.journal_id == journal_id
        ).first()

        if existing:
            existing.role = role
            existing.updated_at = datetime.utcnow()
        else:
            assignment = JournalUserRole(
                user_id=user_id,
                journal_id=journal_id,
                role=role,
                assigned_at=datetime.utcnow()
            )
            self.db.add(assignment)

        self.db.commit()

    def get_user_journals(self, user_id: int) -> List[Dict]:
        """
        Get all journals a user is associated with and their roles.
        """
        from db.models import JournalUserRole, Journal

        assignments = self.db.query(JournalUserRole, Journal).join(
            Journal,
            JournalUserRole.journal_id == Journal.id
        ).filter(
            JournalUserRole.user_id == user_id,
            Journal.is_active == True
        ).all()

        return [
            {
                'journal_id': journal.id,
                'journal_title': journal.title,
                'role': assignment.role,
                'assigned_at': assignment.assigned_at.isoformat()
            }
            for assignment, journal in assignments
        ]

    def get_cross_journal_analytics(self) -> Dict:
        """
        Get aggregated analytics across all journals.
        Useful for publishers managing multiple journals.
        """
        from db.models import Journal, Manuscript, Review

        journals = self.list_journals(active_only=True)

        total_manuscripts = 0
        total_published = 0
        total_reviews = 0
        total_views = 0
        total_downloads = 0

        journal_summaries = []

        for journal in journals:
            stats = self.get_journal_statistics(journal.id)
            total_manuscripts += stats['total_manuscripts']
            total_published += stats['published_articles']
            total_reviews += stats['total_reviews']
            total_views += stats['total_views']
            total_downloads += stats['total_downloads']

            journal_summaries.append({
                'journal_id': journal.id,
                'title': journal.title,
                'manuscripts': stats['total_manuscripts'],
                'published': stats['published_articles']
            })

        return {
            'total_journals': len(journals),
            'total_manuscripts': total_manuscripts,
            'total_published': total_published,
            'total_reviews': total_reviews,
            'total_views': total_views,
            'total_downloads': total_downloads,
            'journal_summaries': journal_summaries
        }

    def clone_journal_settings(
        self,
        source_journal_id: int,
        target_journal_id: int,
        include_users: bool = False
    ) -> None:
        """
        Clone settings from one journal to another.
        Useful when setting up a new journal with similar configuration.
        """
        source = self.get_journal(source_journal_id)
        target = self.get_journal(target_journal_id)

        if not source or not target:
            raise ValueError("Source or target journal not found")

        # Clone branding
        target.branding = source.branding.copy()

        # Clone specializations
        if hasattr(source, 'specializations'):
            for spec in source.specializations:
                # Clone specialization logic here
                pass

        # Clone user assignments if requested
        if include_users:
            from db.models import JournalUserRole

            assignments = self.db.query(JournalUserRole).filter(
                JournalUserRole.journal_id == source_journal_id
            ).all()

            for assignment in assignments:
                new_assignment = JournalUserRole(
                    user_id=assignment.user_id,
                    journal_id=target_journal_id,
                    role=assignment.role,
                    assigned_at=datetime.utcnow()
                )
                self.db.add(new_assignment)

        self.db.commit()


# Add new models to db/models.py
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON

class Journal(Base):
    __tablename__ = "journals"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    short_title = Column(String(100), nullable=False)
    issn = Column(String(20), unique=True, nullable=False, index=True)
    eissn = Column(String(20), unique=True, nullable=False, index=True)
    publisher_name = Column(String(255), nullable=False)
    description = Column(Text)
    subject_areas = Column(JSON)  # List of subject areas
    website_url = Column(String(500))
    email = Column(String(255))
    editor_in_chief_id = Column(Integer, ForeignKey('users.id'))

    # Branding and customization
    branding = Column(JSON)  # Logo, colors, theme
    custom_domain = Column(String(255))

    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deactivated_at = Column(DateTime(timezone=True))

    # Relationships
    manuscripts = relationship("Manuscript", back_populates="journal")
    editor_in_chief = relationship("User")


class JournalUserRole(Base):
    __tablename__ = "journal_user_roles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    journal_id = Column(Integer, ForeignKey('journals.id'), nullable=False)
    role = Column(String(50), nullable=False)  # editor, reviewer, author for this journal
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User")
    journal = relationship("Journal")
"""
