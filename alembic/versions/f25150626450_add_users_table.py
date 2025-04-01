"""add users table

Revision ID: f25150626450
Revises: fc12327ac3ec
Create Date: 2024-04-01 08:52:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = 'f25150626450'
down_revision = 'fc12327ac3ec'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('company', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

def downgrade():
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users') 