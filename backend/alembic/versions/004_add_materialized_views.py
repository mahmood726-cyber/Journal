"""Add materialized views for complex queries

Revision ID: 004
Revises: 003
Create Date: 2025-01-06 14:00:00.000000

Materialized views cache results of expensive queries for instant access.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    """Create materialized views for frequently accessed complex queries."""

    # Materialized view for published articles with all metadata
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS mv_published_articles AS
        SELECT
            m.id,
            m.manuscript_id,
            m.title,
            m.abstract,
            m.keywords,
            m.doi,
            m.published_at,
            m.views,
            m.downloads,
            m.volume,
            m.issue,
            m.page_start,
            m.page_end,
            s.name as specialization_name,
            s.id as specialization_id,
            STRING_AGG(u.full_name, ', ' ORDER BY ma.author_order) as authors,
            STRING_AGG(u.affiliation, '; ' ORDER BY ma.author_order) as affiliations,
            COUNT(DISTINCT r.id) as review_count
        FROM manuscripts m
        LEFT JOIN specializations s ON m.specialization_id = s.id
        LEFT JOIN manuscript_authors ma ON m.id = ma.manuscript_id
        LEFT JOIN users u ON ma.author_id = u.id
        LEFT JOIN reviews r ON m.id = r.manuscript_id
        WHERE m.status = 'published'
        GROUP BY m.id, s.id, s.name
        ORDER BY m.published_at DESC;

        CREATE UNIQUE INDEX idx_mv_published_articles_id ON mv_published_articles(id);
        CREATE INDEX idx_mv_published_articles_published_at ON mv_published_articles(published_at);
        CREATE INDEX idx_mv_published_articles_specialization ON mv_published_articles(specialization_id);
    """)

    # Materialized view for manuscript statistics
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS mv_manuscript_stats AS
        SELECT
            m.id,
            m.manuscript_id,
            m.title,
            m.status,
            m.submitted_at,
            m.published_at,
            COUNT(DISTINCT r.id) as review_count,
            AVG(EXTRACT(EPOCH FROM (r.completed_at - r.assigned_at))/86400)::numeric(10,1) as avg_review_days,
            COUNT(DISTINCT c.id) as comment_count,
            m.views,
            m.downloads,
            CASE
                WHEN m.published_at IS NOT NULL THEN
                    EXTRACT(EPOCH FROM (m.published_at - m.submitted_at))/86400
                ELSE NULL
            END::numeric(10,1) as time_to_publication_days
        FROM manuscripts m
        LEFT JOIN reviews r ON m.id = r.manuscript_id AND r.status = 'completed'
        LEFT JOIN comments c ON m.id = c.manuscript_id
        GROUP BY m.id
        ORDER BY m.created_at DESC;

        CREATE UNIQUE INDEX idx_mv_manuscript_stats_id ON mv_manuscript_stats(id);
        CREATE INDEX idx_mv_manuscript_stats_status ON mv_manuscript_stats(status);
    """)

    # Materialized view for reviewer workload
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS mv_reviewer_workload AS
        SELECT
            u.id as reviewer_id,
            u.full_name,
            u.email,
            u.affiliation,
            COUNT(DISTINCT CASE WHEN r.status = 'pending' THEN r.id END) as pending_reviews,
            COUNT(DISTINCT CASE WHEN r.status = 'in_progress' THEN r.id END) as active_reviews,
            COUNT(DISTINCT CASE WHEN r.status = 'completed' THEN r.id END) as completed_reviews,
            AVG(CASE
                WHEN r.status = 'completed' AND r.completed_at IS NOT NULL THEN
                    EXTRACT(EPOCH FROM (r.completed_at - r.assigned_at))/86400
                ELSE NULL
            END)::numeric(10,1) as avg_review_days,
            MAX(r.due_date) as next_due_date,
            STRING_AGG(DISTINCT s.name, ', ') as specializations
        FROM users u
        INNER JOIN reviews r ON u.id = r.reviewer_id
        LEFT JOIN user_specializations us ON u.id = us.user_id
        LEFT JOIN specializations s ON us.specialization_id = s.id
        WHERE u.role IN ('reviewer', 'associate_editor', 'editor_in_chief')
        GROUP BY u.id, u.full_name, u.email, u.affiliation
        ORDER BY pending_reviews DESC, active_reviews DESC;

        CREATE UNIQUE INDEX idx_mv_reviewer_workload_id ON mv_reviewer_workload(reviewer_id);
        CREATE INDEX idx_mv_reviewer_workload_pending ON mv_reviewer_workload(pending_reviews);
    """)

    # Materialized view for journal metrics
    op.execute("""
        CREATE MATERIALIZED VIEW IF NOT EXISTS mv_journal_metrics AS
        SELECT
            DATE_TRUNC('month', m.submitted_at) as month,
            COUNT(DISTINCT m.id) as total_submissions,
            COUNT(DISTINCT CASE WHEN m.status = 'published' THEN m.id END) as published_count,
            COUNT(DISTINCT CASE WHEN m.status = 'rejected' THEN m.id END) as rejected_count,
            ROUND(
                COUNT(DISTINCT CASE WHEN m.status = 'published' THEN m.id END)::numeric /
                NULLIF(COUNT(DISTINCT m.id), 0) * 100,
                1
            ) as acceptance_rate,
            AVG(
                CASE WHEN m.published_at IS NOT NULL THEN
                    EXTRACT(EPOCH FROM (m.published_at - m.submitted_at))/86400
                END
            )::numeric(10,1) as avg_time_to_publication,
            SUM(m.views) as total_views,
            SUM(m.downloads) as total_downloads
        FROM manuscripts m
        WHERE m.submitted_at IS NOT NULL
        GROUP BY DATE_TRUNC('month', m.submitted_at)
        ORDER BY month DESC;

        CREATE INDEX idx_mv_journal_metrics_month ON mv_journal_metrics(month);
    """)


def downgrade():
    """Drop materialized views."""
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_published_articles CASCADE")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_manuscript_stats CASCADE")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_reviewer_workload CASCADE")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS mv_journal_metrics CASCADE")
