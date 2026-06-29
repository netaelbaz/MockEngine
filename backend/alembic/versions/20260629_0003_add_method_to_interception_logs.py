"""add_method_to_interception_logs

Revision ID: add_method_to_interception_logs
Revises: add_use_mock_backend_to_rules
Create Date: 2026-06-29 00:03:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'add_method_to_interception_logs'
down_revision = 'add_use_mock_backend_to_rules'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('interception_logs', sa.Column('method', sa.String(), nullable=True))


def downgrade():
    op.drop_column('interception_logs', 'method')
