"""connect post and file

Revision ID: e0c6975ec640
Revises: 9719f51321c8
Create Date: 2020-04-05 18:52:32.619831

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e0c6975ec640'
down_revision = '9719f51321c8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('file', sa.Column('post_id', sa.BigInteger(), nullable=False))
    op.create_foreign_key(None, 'file', 'post', ['post_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'file', type_='foreignkey')
    op.drop_column('file', 'post_id')
    # ### end Alembic commands ###
