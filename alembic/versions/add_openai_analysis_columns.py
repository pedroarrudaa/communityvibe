"""add openai analysis columns

Revision ID: add_openai_analysis_columns
Revises: 4b433582f0f3
Create Date: 2024-03-21 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = 'add_openai_analysis_columns'
down_revision = '4b433582f0f3'
branch_labels = None
depends_on = None

def upgrade():
    # Add OpenAI analysis columns
    op.add_column('posts', sa.Column('openai_sentiment', JSONB, nullable=False, server_default='{}'))
    op.add_column('posts', sa.Column('openai_products', JSONB, nullable=False, server_default='{}'))
    op.add_column('posts', sa.Column('openai_categories', JSONB, nullable=False, server_default='{}'))
    op.add_column('posts', sa.Column('openai_confidence', sa.Float(), nullable=True))
    op.add_column('posts', sa.Column('openai_analysis_timestamp', sa.DateTime(timezone=True), nullable=True))

def downgrade():
    # Remove OpenAI analysis columns
    op.drop_column('posts', 'openai_sentiment')
    op.drop_column('posts', 'openai_products')
    op.drop_column('posts', 'openai_categories')
    op.drop_column('posts', 'openai_confidence')
    op.drop_column('posts', 'openai_analysis_timestamp') 