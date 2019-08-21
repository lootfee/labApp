"""empty message

Revision ID: adcb37cb84c7
Revises: 6271d00701ce
Create Date: 2019-08-21 18:32:32.852042

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'adcb37cb84c7'
down_revision = '6271d00701ce'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comment', sa.Column('timestamp', sa.DateTime(), nullable=True))
    op.create_index(op.f('ix_comment_timestamp'), 'comment', ['timestamp'], unique=False)
    op.add_column('comment_reply', sa.Column('timestamp', sa.DateTime(), nullable=True))
    op.create_index(op.f('ix_comment_reply_timestamp'), 'comment_reply', ['timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_comment_reply_timestamp'), table_name='comment_reply')
    op.drop_column('comment_reply', 'timestamp')
    op.drop_index(op.f('ix_comment_timestamp'), table_name='comment')
    op.drop_column('comment', 'timestamp')
    # ### end Alembic commands ###
