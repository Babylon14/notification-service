"""merge heads

Revision ID: 488b49d74775
Revises: 7901b95267e0, ac4d03fdfae6
Create Date: 2026-01-13 08:27:48.771898

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '488b49d74775'
down_revision: Union[str, Sequence[str], None] = ('7901b95267e0', 'ac4d03fdfae6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
