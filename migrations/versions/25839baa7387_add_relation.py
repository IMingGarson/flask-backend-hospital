"""Add relation

Revision ID: 25839baa7387
Revises: 45e2472c24f4
Create Date: 2025-01-10 16:31:08.519221

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '25839baa7387'
down_revision = '45e2472c24f4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('patient_symptom_data', schema=None) as batch_op:
        batch_op.create_foreign_key(None, 'patients', ['patient_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('patient_symptom_data', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')

    # ### end Alembic commands ###
