"""adding chat_id to  usr model

Revision ID: 9591b1b407a4
Revises: 429ed1deb6ee
Create Date: 2025-03-22 17:52:52.410307

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9591b1b407a4'
down_revision: Union[str, None] = '429ed1deb6ee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('chat_id', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'chat_id')
    # ### end Alembic commands ###
