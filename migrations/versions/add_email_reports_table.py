"""add_email_reports_table

Revision ID: 7f23e1fa1697
Revises: 6f23e1fa1696
Create Date: 2023-05-14 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7f23e1fa1697'
down_revision = '6f23e1fa1696'
branch_labels = None
depends_on = None


def upgrade():
    # Créer la table email_reports
    op.create_table('email_reports',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('bank_name', sa.String(), nullable=False),
        sa.Column('subject', sa.String(), nullable=False),
        sa.Column('recipients', sa.JSON(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('scheduled_report_id', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['scheduled_report_id'], ['scheduled_reports.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_email_reports_bank_name'), 'email_reports', ['bank_name'], unique=False)
    op.create_index(op.f('ix_email_reports_id'), 'email_reports', ['id'], unique=False)


def downgrade():
    # Supprimer la table email_reports
    op.drop_index(op.f('ix_email_reports_id'), table_name='email_reports')
    op.drop_index(op.f('ix_email_reports_bank_name'), table_name='email_reports')
    op.drop_table('email_reports') 