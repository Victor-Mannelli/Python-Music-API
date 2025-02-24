"""add: link column to music table

Revision ID: a85685923d55
Revises: 49e78f621afd
Create Date: 2025-02-23 15:03:22.089652

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a85685923d55'
down_revision: Union[str, None] = '49e78f621afd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('musics', sa.Column('link', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('musics', 'link')
    # ### end Alembic commands ###
