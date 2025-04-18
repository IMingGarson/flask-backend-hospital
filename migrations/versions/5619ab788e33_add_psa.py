"""add psa

Revision ID: 5619ab788e33
Revises: 64f5c6279747
Create Date: 2024-12-25 22:20:08.500353

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '5619ab788e33'
down_revision = '64f5c6279747'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('patient_psa_data', schema=None) as batch_op:
        batch_op.add_column(sa.Column('date', sa.String(length=255), nullable=False))
        batch_op.add_column(sa.Column('psa', mysql.FLOAT(unsigned=True), nullable=False))
        batch_op.drop_column('value')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('patient_psa_data', schema=None) as batch_op:
        batch_op.add_column(sa.Column('value', mysql.INTEGER(), autoincrement=False, nullable=False))
        batch_op.drop_column('psa')
        batch_op.drop_column('date')

    # ### end Alembic commands ###
