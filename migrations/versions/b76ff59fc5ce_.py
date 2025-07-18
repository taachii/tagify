"""empty message

Revision ID: b76ff59fc5ce
Revises: ff90bb6e5db2
Create Date: 2025-07-07 14:39:20.005759

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b76ff59fc5ce'
down_revision = 'ff90bb6e5db2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('classifications', schema=None) as batch_op:
        batch_op.drop_column('upload_filename')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('classifications', schema=None) as batch_op:
        batch_op.add_column(sa.Column('upload_filename', sa.VARCHAR(), nullable=True))

    # ### end Alembic commands ###
