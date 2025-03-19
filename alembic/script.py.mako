"""
${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# Revision identifiers, used by Alembic
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade():
    op.alter_column('tasks', 'user_id', type_=sa.dialects.postgresql.UUID(as_uuid=True), nullable=False)
    op.alter_column('users', 'id', type_=sa.dialects.postgresql.UUID(as_uuid=True), nullable=False)

def downgrade():
    op.alter_column('tasks', 'user_id', type_=sa.Integer(), nullable=False)
    op.alter_column('users', 'id', type_=sa.Integer(), nullable=False)
