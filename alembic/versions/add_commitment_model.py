"""add_commitment_model

Revision ID: 3a962f5a1c91
Revises: 7530ac0f785c
Create Date: 2025-03-04 00:00:00.000000

"""
from typing import Sequence, Optional
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3a962f5a1c91'
down_revision = '7530ac0f785c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types
    op.create_table(
        'commitments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('source_reference', sa.String(length=255), nullable=True),
        sa.Column('extracted_from', sa.Text(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=False, default=0.0),
        sa.Column('status', sa.String(length=50), nullable=False, default='detected'),
        sa.Column('priority', sa.String(length=50), nullable=False, default='medium'),
        sa.Column('related_person', sa.String(length=255), nullable=True),
        sa.Column('related_task_id', sa.Integer(), nullable=True),
        sa.Column('detected_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('time_frame', sa.String(length=255), nullable=True),
        sa.Column('action_required', sa.String(length=255), nullable=True),
        sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('should_remind', sa.Boolean(), nullable=False, default=True),
        sa.Column('reminder_frequency', sa.String(length=100), nullable=True),
        sa.Column('cross_references', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['related_task_id'], ['tasks.id'], name='fk_commitment_related_task'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_commitment_user'),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_commitments_user_id', 'user_id'),
        sa.Index('ix_commitments_status', 'status'),
        sa.Index('ix_commitments_detected_at', 'detected_at'),
        sa.Index('ix_commitments_due_date', 'due_date')
    )
    
    # Add related_commitment_id to the reminders table if it doesn't exist
    op.add_column('reminders', sa.Column('related_commitment_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_reminder_commitment', 'reminders', 'commitments', ['related_commitment_id'], ['id'])


def downgrade() -> None:
    # Drop the foreign key on reminders first
    op.drop_constraint('fk_reminder_commitment', 'reminders', type_='foreignkey')
    op.drop_column('reminders', 'related_commitment_id')
    
    # Then drop the commitments table
    op.drop_table('commitments')