"""
Database package initialization.
Import all models here to ensure they are registered with SQLAlchemy.
"""
from .base import Base
from .models import (
    User,
    Specialization,
    Manuscript,
    ManuscriptFile,
    Review,
    EditorialDecision,
    Comment,
    EmailLog,
    AuditLog,
    Theme,
    ThemeRating,
    CopyeditingAssignment,
    ProductionAssignment,
    Issue,
    ArticleStatistics,
    Discussion,
    DiscussionMessage,
    DiscussionAttachment,
    ManuscriptParticipant,
    UserRole,
    ManuscriptStatus,
    ReviewStatus,
    ReviewRecommendation,
    DecisionType
)

# Import DOI models
from .models_doi import (
    DOIDeposit,
    ManuscriptDOI,
    DOIDepositLog,
    DOIStatus
)

# Import metrics models
from .models_metrics import (
    ArticleMetricEvent,
    ArticleMetricSummary,
    JournalMetricSummary,
    ArticleAltmetrics,
    EventType
)

__all__ = [
    'Base',
    # Core models
    'User',
    'Specialization',
    'Manuscript',
    'ManuscriptFile',
    'Review',
    'EditorialDecision',
    'Comment',
    'EmailLog',
    'AuditLog',
    'Theme',
    'ThemeRating',
    'CopyeditingAssignment',
    'ProductionAssignment',
    'Issue',
    'ArticleStatistics',
    'Discussion',
    'DiscussionMessage',
    'DiscussionAttachment',
    'ManuscriptParticipant',
    # Enums
    'UserRole',
    'ManuscriptStatus',
    'ReviewStatus',
    'ReviewRecommendation',
    'DecisionType',
    # DOI models
    'DOIDeposit',
    'ManuscriptDOI',
    'DOIDepositLog',
    'DOIStatus',
    # Metrics models
    'ArticleMetricEvent',
    'ArticleMetricSummary',
    'JournalMetricSummary',
    'ArticleAltmetrics',
    'EventType'
]
