"""rename_delay_ms_to_delay_s

Revision ID: rename_delay_ms_to_delay_s
Revises: add_ai_prompt_to_rules
Create Date: 2026-06-26 00:01:00.000000

"""
from alembic import op


revision = 'rename_delay_ms_to_delay_s'
down_revision = 'add_ai_prompt_to_rules'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('rules', 'delay_ms', new_column_name='delay_s')


def downgrade() -> None:
    op.alter_column('rules', 'delay_s', new_column_name='delay_ms')
