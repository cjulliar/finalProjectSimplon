"""Ajout de la table bank_data_raw

Revision ID: 7f23e1fa1697
Revises: 6f23e1fa1696
Create Date: 2025-05-14 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '7f23e1fa1697'
down_revision = '6f23e1fa1696'
branch_labels = None
depends_on = None


def upgrade():
    # Créer la table bank_data_raw
    op.create_table('bank_data_raw',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('week_id', sa.String(), nullable=False),
        sa.Column('group_name', sa.String(), nullable=False),
        sa.Column('bank_name', sa.String(), nullable=False),
        sa.Column('raw_data', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bank_data_raw_bank_name'), 'bank_data_raw', ['bank_name'], unique=False)
    op.create_index(op.f('ix_bank_data_raw_group_name'), 'bank_data_raw', ['group_name'], unique=False)
    op.create_index(op.f('ix_bank_data_raw_id'), 'bank_data_raw', ['id'], unique=False)
    op.create_index(op.f('ix_bank_data_raw_week_id'), 'bank_data_raw', ['week_id'], unique=False)


def downgrade():
    # Supprimer la table bank_data_raw
    op.drop_index(op.f('ix_bank_data_raw_week_id'), table_name='bank_data_raw')
    op.drop_index(op.f('ix_bank_data_raw_id'), table_name='bank_data_raw')
    op.drop_index(op.f('ix_bank_data_raw_group_name'), table_name='bank_data_raw')
    op.drop_index(op.f('ix_bank_data_raw_bank_name'), table_name='bank_data_raw')
    op.drop_table('bank_data_raw') 