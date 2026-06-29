"""add_users_table_and_user_id_to_api_keys

Revision ID: add_users_and_user_id
Revises: add_unique_constraint_to_rule_name
Create Date: 2026-06-27 00:01:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'add_users_and_user_id'
down_revision = 'add_unique_constraint_to_rule_name'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    with op.batch_alter_table('api_keys') as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_api_keys_user_id', 'users', ['user_id'], ['id'])


def downgrade() -> None:
    with op.batch_alter_table('api_keys') as batch_op:
        batch_op.drop_constraint('fk_api_keys_user_id', type_='foreignkey')
        batch_op.drop_column('user_id')

    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
