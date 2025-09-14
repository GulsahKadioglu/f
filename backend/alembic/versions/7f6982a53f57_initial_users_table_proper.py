"""Initial users table proper."""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7f6982a53f57"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Apply upgrade migration for initial users table."""
    op.create_table(
        "users",
        sa.Column(
            "id",
            sa.UUID(),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("email", sa.String(), unique=True, nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column(
            "is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False
        ),
        sa.Column(
            "role", sa.String(), server_default=sa.text("'doctor'"), nullable=False
        ),
        sa.Column("push_token", sa.String(), nullable=True),
        sa.Column("mfa_secret", sa.String(), nullable=True),
        sa.Column(
            "mfa_enabled", sa.Boolean(), server_default=sa.text("false"), nullable=False
        ),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)


def downgrade() -> None:
    """Revert downgrade migration for initial users table."""
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
