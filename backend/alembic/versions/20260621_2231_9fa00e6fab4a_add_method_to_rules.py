"""add_method_to_rules

Revision ID: 9fa00e6fab4a
Revises: 51ef119722f9
Create Date: 2026-06-21 22:31:28.697666

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9fa00e6fab4a'
down_revision = '51ef119722f9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('rules', sa.Column('method', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('rules', 'method')
