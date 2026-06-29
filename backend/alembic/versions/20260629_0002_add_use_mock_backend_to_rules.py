"""add_use_mock_backend_to_rules

Revision ID: add_use_mock_backend_to_rules
Revises: add_name_fields_to_users
Create Date: 2026-06-29 00:02:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'add_use_mock_backend_to_rules'
down_revision = 'add_name_fields_to_users'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('rules', sa.Column('use_mock_backend', sa.Boolean(), nullable=False, server_default='1'))


def downgrade():
    op.drop_column('rules', 'use_mock_backend')
