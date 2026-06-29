"""make_status_code_nullable_in_rules

Revision ID: make_status_code_nullable_in_rules
Revises: add_method_to_interception_logs
Create Date: 2026-06-29 00:04:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'make_status_code_nullable_in_rules'
down_revision = 'add_method_to_interception_logs'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('rules') as batch_op:
        batch_op.alter_column('status_code', nullable=True)


def downgrade():
    with op.batch_alter_table('rules') as batch_op:
        batch_op.alter_column('status_code', nullable=False)
