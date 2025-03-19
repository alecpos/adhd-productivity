"""


Revision ID: 7530ac0f785c
Revises: 27401518c139
Create Date: 2025-02-02 12:18:18.098530

"""

# Revision identifiers, used by Alembic
revision: str = "7530ac0f785c"
down_revision: Union[str, None] = "27401518c139"
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
