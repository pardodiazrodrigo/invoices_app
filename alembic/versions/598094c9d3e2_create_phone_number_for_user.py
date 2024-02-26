"""Create phone number for user

Revision ID: 598094c9d3e2
Revises: 
Create Date: 2024-02-26 14:34:51.732091

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '598094c9d3e2'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('user', sa.Column('phone_number', sa.String(), nullable=True))
    pass


def downgrade() -> None:
    op.drop_column('user', 'phone_number')
