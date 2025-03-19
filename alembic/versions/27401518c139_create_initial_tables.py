"""


Revision ID: 27401518c139
Revises:
Create Date: 2025-02-01 16:29:13.319515

"""

# Revision identifiers, used by Alembic
revision: str = "27401518c139"
down_revision: Union[str, None] = None
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
