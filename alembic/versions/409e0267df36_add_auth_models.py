"""add auth models

Revision ID: 409e0267df36
Revises: 27401518c139
Create Date: 2024-02-04 05:44:00.000000

"""

from typing import Union, Sequence
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "409e0267df36"
down_revision: Union[str, None] = "27401518c139"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, None] = None


def upgrade() -> None:
    op.alter_column(
        "tasks",
        "user_id",
        type_=sa.dialects.postgresql.UUID(as_uuid=True),
        nullable=False,
    )
    op.alter_column("users", "id", type_=sa.dialects.postgresql.UUID(as_uuid=True), nullable=False)


def downgrade() -> None:
    op.alter_column("tasks", "user_id", type_=sa.Integer(), nullable=False)
    op.alter_column("users", "id", type_=sa.Integer(), nullable=False)
