"""Merge heads.

Revision ID: c9150c829033
Revises: 1a2b3c4d5e6f, a1b2c3d4e5f6
Create Date: 2025-08-17 16:16:07.909390

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "c9150c829033"
down_revision: Union[str, None] = ("1a2b3c4d5e6f", "a1b2c3d4e5f6")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Apply database migrations."""
    pass


def downgrade() -> None:
    """Revert database migrations."""
    pass
