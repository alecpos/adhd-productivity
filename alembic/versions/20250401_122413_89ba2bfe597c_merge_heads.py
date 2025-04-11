"""
merge heads

Revision ID: 89ba2bfe597c
Revises: 2f993fbd1f72, 3a962f5a1c91
Create Date: 2025-04-01 12:24:13.767847+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic
revision: str = '89ba2bfe597c'
down_revision: Union[str, None] = ('2f993fbd1f72', '3a962f5a1c91')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column('tasks', 'user_id', type_=sa.dialects.postgresql.UUID(as_uuid=True), nullable=False)
    op.alter_column('users', 'id', type_=sa.dialects.postgresql.UUID(as_uuid=True), nullable=False)

def downgrade():
    op.alter_column('tasks', 'user_id', type_=sa.Integer(), nullable=False)
    op.alter_column('users', 'id', type_=sa.Integer(), nullable=False)
