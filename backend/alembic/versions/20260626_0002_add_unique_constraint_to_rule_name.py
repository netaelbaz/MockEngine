"""add_unique_constraint_to_rule_name

Revision ID: add_unique_constraint_to_rule_name
Revises: rename_delay_ms_to_delay_s
Create Date: 2026-06-26 00:02:00.000000

"""
from alembic import op


revision = 'add_unique_constraint_to_rule_name'
down_revision = 'rename_delay_ms_to_delay_s'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('rules') as batch_op:
        batch_op.create_unique_constraint('uq_rules_name', ['name'])


def downgrade() -> None:
    with op.batch_alter_table('rules') as batch_op:
        batch_op.drop_constraint('uq_rules_name', type_='unique')
