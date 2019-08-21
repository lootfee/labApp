"""created m2m table for order order_creator order_submitted_by

Revision ID: a6728dc4eec8
Revises: 3cabcb6ec168
Create Date: 2019-08-03 12:08:16.763013

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'a6728dc4eec8'
down_revision = '3cabcb6ec168'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('order_creator',
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['order_id'], ['order.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], )
    )
    op.create_table('order_submitted_by',
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['order_id'], ['order.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], )
    )
    op.drop_constraint('order_ibfk_2', 'order', type_='foreignkey')
    op.drop_constraint('order_ibfk_3', 'order', type_='foreignkey')
    op.drop_column('order', 'order_creator')
    op.drop_column('order', 'submitted_by')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('order', sa.Column('submitted_by', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.add_column('order', sa.Column('order_creator', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True))
    op.create_foreign_key('order_ibfk_3', 'order', 'user', ['order_creator'], ['id'])
    op.create_foreign_key('order_ibfk_2', 'order', 'user', ['submitted_by'], ['id'])
    op.drop_table('order_submitted_by')
    op.drop_table('order_creator')
    # ### end Alembic commands ###