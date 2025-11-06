"""Add COUNTER metrics models

Revision ID: 002_metrics
Revises: 001_doi_tracking
Create Date: 2025-01-06

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_metrics'
down_revision = '001_doi_tracking'
branch_labels = None
depends_on = None


def upgrade():
    # Create article_metric_events table
    op.create_table('article_metric_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('manuscript_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('event_date', sa.Date(), nullable=False),
        sa.Column('event_timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('session_id', sa.String(length=100), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('country_code', sa.String(length=2), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('region', sa.String(length=100), nullable=True),
        sa.Column('referrer', sa.Text(), nullable=True),
        sa.Column('referrer_category', sa.String(length=50), nullable=True),
        sa.Column('is_robot', sa.Boolean(), nullable=True),
        sa.Column('is_unique', sa.Boolean(), nullable=True),
        sa.Column('is_double_click', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['manuscript_id'], ['manuscripts.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_article_metric_events_manuscript_id'), 'article_metric_events', ['manuscript_id'], unique=False)
    op.create_index(op.f('ix_article_metric_events_event_type'), 'article_metric_events', ['event_type'], unique=False)
    op.create_index(op.f('ix_article_metric_events_event_date'), 'article_metric_events', ['event_date'], unique=False)
    op.create_index(op.f('ix_article_metric_events_event_timestamp'), 'article_metric_events', ['event_timestamp'], unique=False)
    op.create_index(op.f('ix_article_metric_events_session_id'), 'article_metric_events', ['session_id'], unique=False)
    op.create_index(op.f('ix_article_metric_events_country_code'), 'article_metric_events', ['country_code'], unique=False)

    # Create article_metric_summaries table
    op.create_table('article_metric_summaries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('manuscript_id', sa.Integer(), nullable=False),
        sa.Column('metric_date', sa.Date(), nullable=False),
        sa.Column('total_item_requests', sa.Integer(), nullable=True),
        sa.Column('unique_item_requests', sa.Integer(), nullable=True),
        sa.Column('total_item_investigations', sa.Integer(), nullable=True),
        sa.Column('unique_item_investigations', sa.Integer(), nullable=True),
        sa.Column('abstract_views', sa.Integer(), nullable=True),
        sa.Column('full_text_views', sa.Integer(), nullable=True),
        sa.Column('pdf_downloads', sa.Integer(), nullable=True),
        sa.Column('xml_downloads', sa.Integer(), nullable=True),
        sa.Column('html_views', sa.Integer(), nullable=True),
        sa.Column('top_countries', sa.Text(), nullable=True),
        sa.Column('referrer_breakdown', sa.Text(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['manuscript_id'], ['manuscripts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_article_metric_summaries_manuscript_id'), 'article_metric_summaries', ['manuscript_id'], unique=False)
    op.create_index(op.f('ix_article_metric_summaries_metric_date'), 'article_metric_summaries', ['metric_date'], unique=False)

    # Create journal_metric_summaries table
    op.create_table('journal_metric_summaries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('month', sa.Integer(), nullable=False),
        sa.Column('total_item_requests', sa.Integer(), nullable=True),
        sa.Column('unique_item_requests', sa.Integer(), nullable=True),
        sa.Column('total_item_investigations', sa.Integer(), nullable=True),
        sa.Column('unique_item_investigations', sa.Integer(), nullable=True),
        sa.Column('articles_published', sa.Integer(), nullable=True),
        sa.Column('articles_with_activity', sa.Integer(), nullable=True),
        sa.Column('top_articles', sa.Text(), nullable=True),
        sa.Column('countries_reached', sa.Integer(), nullable=True),
        sa.Column('top_countries', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_journal_metric_summaries_year'), 'journal_metric_summaries', ['year'], unique=False)
    op.create_index(op.f('ix_journal_metric_summaries_month'), 'journal_metric_summaries', ['month'], unique=False)

    # Create article_altmetrics table
    op.create_table('article_altmetrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('manuscript_id', sa.Integer(), nullable=False),
        sa.Column('crossref_citations', sa.Integer(), nullable=True),
        sa.Column('scopus_citations', sa.Integer(), nullable=True),
        sa.Column('google_scholar_citations', sa.Integer(), nullable=True),
        sa.Column('twitter_mentions', sa.Integer(), nullable=True),
        sa.Column('facebook_shares', sa.Integer(), nullable=True),
        sa.Column('linkedin_shares', sa.Integer(), nullable=True),
        sa.Column('reddit_mentions', sa.Integer(), nullable=True),
        sa.Column('mendeley_readers', sa.Integer(), nullable=True),
        sa.Column('researchgate_reads', sa.Integer(), nullable=True),
        sa.Column('news_mentions', sa.Integer(), nullable=True),
        sa.Column('blog_mentions', sa.Integer(), nullable=True),
        sa.Column('altmetric_score', sa.Integer(), nullable=True),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['manuscript_id'], ['manuscripts.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('manuscript_id')
    )


def downgrade():
    op.drop_table('article_altmetrics')
    op.drop_index(op.f('ix_journal_metric_summaries_month'), table_name='journal_metric_summaries')
    op.drop_index(op.f('ix_journal_metric_summaries_year'), table_name='journal_metric_summaries')
    op.drop_table('journal_metric_summaries')
    op.drop_index(op.f('ix_article_metric_summaries_metric_date'), table_name='article_metric_summaries')
    op.drop_index(op.f('ix_article_metric_summaries_manuscript_id'), table_name='article_metric_summaries')
    op.drop_table('article_metric_summaries')
    op.drop_index(op.f('ix_article_metric_events_country_code'), table_name='article_metric_events')
    op.drop_index(op.f('ix_article_metric_events_session_id'), table_name='article_metric_events')
    op.drop_index(op.f('ix_article_metric_events_event_timestamp'), table_name='article_metric_events')
    op.drop_index(op.f('ix_article_metric_events_event_date'), table_name='article_metric_events')
    op.drop_index(op.f('ix_article_metric_events_event_type'), table_name='article_metric_events')
    op.drop_index(op.f('ix_article_metric_events_manuscript_id'), table_name='article_metric_events')
    op.drop_table('article_metric_events')
