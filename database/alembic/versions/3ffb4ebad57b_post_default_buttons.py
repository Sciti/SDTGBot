"""post default buttons

Revision ID: 3ffb4ebad57b
Revises: a1b2c3d4e5f6
Create Date: 2025-06-22 15:23:35.482290

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3ffb4ebad57b'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'posts',
        sa.Column('use_default_buttons', sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.alter_column('posts', 'use_default_buttons', server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('posts', 'use_default_buttons')
