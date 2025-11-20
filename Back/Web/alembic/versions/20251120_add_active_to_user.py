"""
Add active column to user

Revision ID: add_active_20251120
Revises: 20251119_add_perplexity_burstiness_to_analysis_record
Create Date: 2025-11-20
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_active_20251120'
down_revision = 'add_perplexity_burstiness_20251119'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add 'active' column with default True
    with op.batch_alter_table('user') as batch_op:
        batch_op.add_column(sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.text('1')))
    # Remove server_default after backfilling defaults (SQLite keeps literal)
    with op.batch_alter_table('user') as batch_op:
        batch_op.alter_column('active', server_default=None)


def downgrade() -> None:
    with op.batch_alter_table('user') as batch_op:
        batch_op.drop_column('active')
