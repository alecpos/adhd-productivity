"""


Revision ID: 409e0267df36
Revises: 2f993fbd1f72
Create Date: 2025-02-02 12:33:54.261982

"""

# Revision identifiers, used by Alembic
revision: str = "409e0267df36"
down_revision: Union[str, None] = "2f993fbd1f72"
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
