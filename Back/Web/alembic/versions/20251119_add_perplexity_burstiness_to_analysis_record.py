"""
Add perplexity_score and burstiness_score columns to analysis_record

Revision ID: add_perplexity_burstiness_20251119
Revises: 
Create Date: 2025-11-19
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_perplexity_burstiness_20251119'
down_revision = 'bf4638d3da59'
branch_labels = None
depends_on = None

def upgrade():
    try:
        op.add_column('analysisrecord', sa.Column('perplexity_score', sa.Float(), nullable=True))
    except Exception:
        pass
    try:
        op.add_column('analysisrecord', sa.Column('burstiness_score', sa.Float(), nullable=True))
    except Exception:
        pass


def downgrade():
    try:
        op.drop_column('analysisrecord', 'perplexity_score')
    except Exception:
        pass
    try:
        op.drop_column('analysisrecord', 'burstiness_score')
    except Exception:
        pass
