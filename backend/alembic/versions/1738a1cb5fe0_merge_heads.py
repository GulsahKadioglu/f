"""Merge heads

Revision ID: 1738a1cb5fe0
Revises: 17a25cefa5db, d534e8ebeab7
Create Date: 2025-08-27 16:28:04.331412

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1738a1cb5fe0'
down_revision: Union[str, None] = ('17a25cefa5db', 'd534e8ebeab7')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
