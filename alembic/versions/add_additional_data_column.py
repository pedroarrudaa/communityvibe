"""add additional_data column

Revision ID: add_additional_data_column
Revises: previous_revision_id
Create Date: 2024-03-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = 'add_additional_data_column'
down_revision = None  # Update this with your previous migration ID
branch_labels = None
depends_on = None

def upgrade():
    # Add the additional_data column with JSONB type
    op.add_column('posts', sa.Column('additional_data', JSONB, nullable=False, server_default='{}'))

def downgrade():
    # Remove the additional_data column
    op.drop_column('posts', 'additional_data') 