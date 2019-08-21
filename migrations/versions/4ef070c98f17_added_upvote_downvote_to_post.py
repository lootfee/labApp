"""added upvote downvote to post

Revision ID: 4ef070c98f17
Revises: a86b19755316
Create Date: 2019-08-20 19:57:40.324767

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4ef070c98f17'
down_revision = 'a86b19755316'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('post', sa.Column('downvote', sa.Integer(), nullable=True))
    op.add_column('post', sa.Column('upvote', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('post', 'upvote')
    op.drop_column('post', 'downvote')
    # ### end Alembic commands ###