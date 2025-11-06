"""Add performance indexes for frequently queried fields

Revision ID: 003
Revises: 002
Create Date: 2025-01-06 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    """Add performance-critical indexes."""

    # Manuscripts table indexes
    op.create_index('idx_manuscripts_status', 'manuscripts', ['status'])
    op.create_index('idx_manuscripts_submitter_status', 'manuscripts', ['submitter_id', 'status'])
    op.create_index('idx_manuscripts_specialization_status', 'manuscripts', ['specialization_id', 'status'])
    op.create_index('idx_manuscripts_submitted_at', 'manuscripts', ['submitted_at'])
    op.create_index('idx_manuscripts_published_at', 'manuscripts', ['published_at'])
    op.create_index('idx_manuscripts_created_at', 'manuscripts', ['created_at'])

    # Reviews table indexes
    op.create_index('idx_reviews_manuscript_id', 'reviews', ['manuscript_id'])
    op.create_index('idx_reviews_reviewer_id', 'reviews', ['reviewer_id'])
    op.create_index('idx_reviews_status', 'reviews', ['status'])
    op.create_index('idx_reviews_reviewer_status', 'reviews', ['reviewer_id', 'status'])
    op.create_index('idx_reviews_manuscript_status', 'reviews', ['manuscript_id', 'status'])
    op.create_index('idx_reviews_due_date', 'reviews', ['due_date'])

    # Users table additional indexes
    op.create_index('idx_users_role', 'users', ['role'])
    op.create_index('idx_users_is_active', 'users', ['is_active'])
    op.create_index('idx_users_role_active', 'users', ['role', 'is_active'])
    op.create_index('idx_users_created_at', 'users', ['created_at'])

    # Editorial decisions indexes
    op.create_index('idx_editorial_decisions_manuscript_id', 'editorial_decisions', ['manuscript_id'])
    op.create_index('idx_editorial_decisions_editor_id', 'editorial_decisions', ['editor_id'])
    op.create_index('idx_editorial_decisions_decision_date', 'editorial_decisions', ['decision_date'])

    # Comments table indexes
    op.create_index('idx_comments_manuscript_id', 'comments', ['manuscript_id'])
    op.create_index('idx_comments_user_id', 'comments', ['user_id'])
    op.create_index('idx_comments_created_at', 'comments', ['created_at'])

    # Manuscript files indexes
    op.create_index('idx_manuscript_files_type', 'manuscript_files', ['file_type'])
    op.create_index('idx_manuscript_files_uploaded_at', 'manuscript_files', ['uploaded_at'])

    # Article statistics indexes
    op.create_index('idx_article_stats_manuscript_id', 'article_statistics', ['manuscript_id'])
    op.create_index('idx_article_stats_date', 'article_statistics', ['date'])

    # Discussion indexes
    op.create_index('idx_discussions_manuscript_id', 'discussions', ['manuscript_id'])
    op.create_index('idx_discussions_created_at', 'discussions', ['created_at'])
    op.create_index('idx_discussions_updated_at', 'discussions', ['updated_at'])

    # Manuscript participants indexes
    op.create_index('idx_manuscript_participants_user_id', 'manuscript_participants', ['user_id'])
    op.create_index('idx_manuscript_participants_role', 'manuscript_participants', ['role'])

    # Issues indexes
    op.create_index('idx_issues_volume_number', 'issues', ['volume', 'number'])
    op.create_index('idx_issues_published_at', 'issues', ['published_at'])
    op.create_index('idx_issues_status', 'issues', ['status'])

    # Copyediting assignments indexes
    op.create_index('idx_copyediting_status', 'copyediting_assignments', ['status'])
    op.create_index('idx_copyediting_copyeditor_id', 'copyediting_assignments', ['copyeditor_id'])
    op.create_index('idx_copyediting_due_date', 'copyediting_assignments', ['due_date'])

    # Production assignments indexes
    op.create_index('idx_production_status', 'production_assignments', ['status'])
    op.create_index('idx_production_layout_editor_id', 'production_assignments', ['layout_editor_id'])
    op.create_index('idx_production_due_date', 'production_assignments', ['due_date'])

    # Composite indexes for common queries
    op.create_index(
        'idx_manuscripts_issue_order',
        'manuscripts',
        ['issue_id', 'article_order']
    )
    op.create_index(
        'idx_manuscripts_volume_issue',
        'manuscripts',
        ['volume', 'issue']
    )


def downgrade():
    """Remove performance indexes."""

    # Manuscripts indexes
    op.drop_index('idx_manuscripts_status')
    op.drop_index('idx_manuscripts_submitter_status')
    op.drop_index('idx_manuscripts_specialization_status')
    op.drop_index('idx_manuscripts_submitted_at')
    op.drop_index('idx_manuscripts_published_at')
    op.drop_index('idx_manuscripts_created_at')
    op.drop_index('idx_manuscripts_issue_order')
    op.drop_index('idx_manuscripts_volume_issue')

    # Reviews indexes
    op.drop_index('idx_reviews_manuscript_id')
    op.drop_index('idx_reviews_reviewer_id')
    op.drop_index('idx_reviews_status')
    op.drop_index('idx_reviews_reviewer_status')
    op.drop_index('idx_reviews_manuscript_status')
    op.drop_index('idx_reviews_due_date')

    # Users indexes
    op.drop_index('idx_users_role')
    op.drop_index('idx_users_is_active')
    op.drop_index('idx_users_role_active')
    op.drop_index('idx_users_created_at')

    # Editorial decisions indexes
    op.drop_index('idx_editorial_decisions_manuscript_id')
    op.drop_index('idx_editorial_decisions_editor_id')
    op.drop_index('idx_editorial_decisions_decision_date')

    # Comments indexes
    op.drop_index('idx_comments_manuscript_id')
    op.drop_index('idx_comments_user_id')
    op.drop_index('idx_comments_created_at')

    # Manuscript files indexes
    op.drop_index('idx_manuscript_files_type')
    op.drop_index('idx_manuscript_files_uploaded_at')

    # Article statistics indexes
    op.drop_index('idx_article_stats_manuscript_id')
    op.drop_index('idx_article_stats_date')

    # Discussion indexes
    op.drop_index('idx_discussions_manuscript_id')
    op.drop_index('idx_discussions_created_at')
    op.drop_index('idx_discussions_updated_at')

    # Manuscript participants indexes
    op.drop_index('idx_manuscript_participants_user_id')
    op.drop_index('idx_manuscript_participants_role')

    # Issues indexes
    op.drop_index('idx_issues_volume_number')
    op.drop_index('idx_issues_published_at')
    op.drop_index('idx_issues_status')

    # Copyediting assignments indexes
    op.drop_index('idx_copyediting_status')
    op.drop_index('idx_copyediting_copyeditor_id')
    op.drop_index('idx_copyediting_due_date')

    # Production assignments indexes
    op.drop_index('idx_production_status')
    op.drop_index('idx_production_layout_editor_id')
    op.drop_index('idx_production_due_date')
