"""code datetime default

Revision ID: eb4a2a54080b
Revises: 5c0855df0cd1
Create Date: 2025-06-19 10:15:55.701110

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eb4a2a54080b'
down_revision: Union[str, Sequence[str], None] = '5c0855df0cd1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('registration_codes', 'created_at', server_default=sa.func.current_timestamp())


def downgrade() -> None:
    """Downgrade schema."""
    pass
