"""Add DOI tracking models

Revision ID: 001_doi_tracking
Revises:
Create Date: 2025-01-06

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_doi_tracking'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create DOI status enum
    op.execute("CREATE TYPE doistatus AS ENUM ('pending', 'submitted', 'success', 'failed', 'warning')")

    # Create doi_deposits table
    op.create_table('doi_deposits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('batch_id', sa.String(length=100), nullable=False),
        sa.Column('submission_id', sa.String(length=100), nullable=True),
        sa.Column('manuscript_ids', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('pending', 'submitted', 'success', 'failed', 'warning', name='doistatus'), nullable=True),
        sa.Column('response_message', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('records_total', sa.Integer(), nullable=True),
        sa.Column('records_success', sa.Integer(), nullable=True),
        sa.Column('records_failed', sa.Integer(), nullable=True),
        sa.Column('xml_content', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('environment', sa.String(length=20), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_doi_deposits_batch_id'), 'doi_deposits', ['batch_id'], unique=True)
    op.create_index(op.f('ix_doi_deposits_submission_id'), 'doi_deposits', ['submission_id'], unique=False)
    op.create_index(op.f('ix_doi_deposits_status'), 'doi_deposits', ['status'], unique=False)

    # Create manuscript_dois table
    op.create_table('manuscript_dois',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('manuscript_id', sa.Integer(), nullable=False),
        sa.Column('doi', sa.String(length=255), nullable=False),
        sa.Column('doi_url', sa.String(length=500), nullable=True),
        sa.Column('status', sa.Enum('pending', 'submitted', 'success', 'failed', 'warning', name='doistatus'), nullable=True),
        sa.Column('deposit_id', sa.Integer(), nullable=True),
        sa.Column('registered_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['manuscript_id'], ['manuscripts.id'], ),
        sa.ForeignKeyConstraint(['deposit_id'], ['doi_deposits.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('manuscript_id'),
        sa.UniqueConstraint('doi')
    )
    op.create_index(op.f('ix_manuscript_dois_doi'), 'manuscript_dois', ['doi'], unique=True)

    # Create doi_deposit_logs table
    op.create_table('doi_deposit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('deposit_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('status_before', sa.String(length=50), nullable=True),
        sa.Column('status_after', sa.String(length=50), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('performed_by_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['deposit_id'], ['doi_deposits.id'], ),
        sa.ForeignKeyConstraint(['performed_by_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('doi_deposit_logs')
    op.drop_index(op.f('ix_manuscript_dois_doi'), table_name='manuscript_dois')
    op.drop_table('manuscript_dois')
    op.drop_index(op.f('ix_doi_deposits_status'), table_name='doi_deposits')
    op.drop_index(op.f('ix_doi_deposits_submission_id'), table_name='doi_deposits')
    op.drop_index(op.f('ix_doi_deposits_batch_id'), table_name='doi_deposits')
    op.drop_table('doi_deposits')
    op.execute('DROP TYPE doistatus')
