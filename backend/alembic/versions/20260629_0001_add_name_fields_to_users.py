"""add_name_fields_to_users

Revision ID: add_name_fields_to_users
Revises: add_users_and_user_id
Create Date: 2026-06-29 00:01:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = 'add_name_fields_to_users'
down_revision = 'add_users_and_user_id'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('first_name', sa.String(), nullable=False, server_default=''))
    op.add_column('users', sa.Column('last_name', sa.String(), nullable=False, server_default=''))


def downgrade():
    op.drop_column('users', 'first_name')
    op.drop_column('users', 'last_name')
