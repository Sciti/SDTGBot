"""post buttons and caption placement

Revision ID: a1b2c3d4e5f6
Revises: d1a3b0f46455
Create Date: 2025-06-25 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'd1a3b0f46455'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('caption_above', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('posts', sa.Column('buttons', sa.JSON(), nullable=True))
    op.alter_column('posts', 'caption_above', server_default=None)


def downgrade() -> None:
    op.drop_column('posts', 'buttons')
    op.drop_column('posts', 'caption_above')
