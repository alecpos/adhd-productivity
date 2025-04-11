"""


Revision ID: 7530ac0f785c
Revises: 409e0267df36
Create Date: 2024-02-04 05:44:00.000000

"""
from typing import Union, Sequence
from alembic import op
import sqlalchemy as sa


# Revision identifiers, used by Alembic
revision: str = "7530ac0f785c"
down_revision: Union[str, None] = "409e0267df36"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, None] = None


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
