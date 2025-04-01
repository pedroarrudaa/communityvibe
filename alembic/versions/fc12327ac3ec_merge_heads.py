"""merge heads

Revision ID: fc12327ac3ec
Revises: add_additional_data_column, add_openai_analysis_columns
Create Date: 2025-04-01 10:56:04.412067

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fc12327ac3ec'
down_revision = ('add_additional_data_column', 'add_openai_analysis_columns')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass 