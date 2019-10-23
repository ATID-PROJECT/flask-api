"""empty message

Revision ID: f86d2d0838f9
Revises: 869614dc542a
Create Date: 2019-10-23 07:54:35.676033

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f86d2d0838f9'
down_revision = '869614dc542a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_log', sa.Column('network_id', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user_log', 'network_id')
    # ### end Alembic commands ###