"""Empty message."""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "70c3ed387da4"
down_revision: Union[str, None] = "c9150c829033"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Apply upgrade migration."""
    pass


def downgrade() -> None:
    """Revert downgrade migration."""
    pass
