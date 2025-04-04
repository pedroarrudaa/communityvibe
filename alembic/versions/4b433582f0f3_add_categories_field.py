"""add_categories_field

Revision ID: 4b433582f0f3
Revises: 0cba16788431
Create Date: 2025-03-31 22:58:25.841388

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4b433582f0f3'
down_revision = '0cba16788431'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('categories', sa.JSON(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'categories')
    # ### end Alembic commands ### 