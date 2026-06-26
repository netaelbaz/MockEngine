"""add_ai_prompt_to_rules

Revision ID: add_ai_prompt_to_rules
Revises: 9fa00e6fab4a
Create Date: 2026-06-22 00:01:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'add_ai_prompt_to_rules'
down_revision = '9fa00e6fab4a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('rules', sa.Column('ai_prompt', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('rules', 'ai_prompt')
