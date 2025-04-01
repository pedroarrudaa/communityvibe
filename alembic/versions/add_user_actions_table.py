"""add user actions table

Revision ID: add_user_actions_table
Revises: 4b433582f0f3
Create Date: 2024-04-01 09:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_user_actions_table'
down_revision = '4b433582f0f3'
branch_labels = None
depends_on = None

def upgrade():
    # Create user_actions table
    op.create_table(
        'user_actions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('post_id', sa.Integer(), nullable=False),
        sa.Column('action_type', postgresql.ENUM('view', 'like', 'save', 'share', 'report', 'comment', 'follow', 'unfollow', 'mute', 'block', name='actiontype', create_type=False), nullable=False),
        sa.Column('metadata', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_user_actions_id'), 'user_actions', ['id'], unique=False)
    op.create_index(op.f('ix_user_actions_user_id'), 'user_actions', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_actions_post_id'), 'user_actions', ['post_id'], unique=False)

def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_user_actions_post_id'), table_name='user_actions')
    op.drop_index(op.f('ix_user_actions_user_id'), table_name='user_actions')
    op.drop_index(op.f('ix_user_actions_id'), table_name='user_actions')
    
    # Drop table
    op.drop_table('user_actions') 