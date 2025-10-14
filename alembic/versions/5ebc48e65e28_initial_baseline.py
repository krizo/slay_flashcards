"""Initial baseline

Revision ID: 5ebc48e65e28
Revises: 
Create Date: 2025-10-14 23:51:43.477329

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5ebc48e65e28'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Initial baseline migration.
    This migration does nothing - it just marks the starting point
    for future database schema changes.
    """
    pass


def downgrade() -> None:
    """Downgrade does nothing for baseline migration."""
    pass
