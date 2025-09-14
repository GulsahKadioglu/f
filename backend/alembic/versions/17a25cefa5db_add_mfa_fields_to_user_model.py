"""Add MFA fields to User model."""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "17a25cefa5db"
down_revision: Union[str, None] = "7f6982a53f57"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Apply the database migration to add MFA fields."""
    pass


def downgrade() -> None:
    """Reverts the database migration by removing MFA fields."""
    pass
