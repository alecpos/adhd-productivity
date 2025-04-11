"""


Revision ID: 2f993fbd1f72
Revises: 7530ac0f785c
Create Date: 2025-02-02 12:24:48.424196

"""
from typing import Union, Sequence
from alembic import op
import sqlalchemy as sa


# Revision identifiers, used by Alembic
revision: str = "2f993fbd1f72"
down_revision: Union[str, None] = "7530ac0f785c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.alter_column(
        "tasks",
        "user_id",
        type_=sa.dialects.postgresql.UUID(as_uuid=True),
        nullable=False,
    )
    op.alter_column("users", "id", type_=sa.dialects.postgresql.UUID(as_uuid=True), nullable=False)


def downgrade():
    op.alter_column("tasks", "user_id", type_=sa.Integer(), nullable=False)
    op.alter_column("users", "id", type_=sa.Integer(), nullable=False)
