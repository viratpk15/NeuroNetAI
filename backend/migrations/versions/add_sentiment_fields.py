"""Add missing fields to sentiment_results table

Revision ID: add_sentiment_fields
Revises: 
Create Date: 2024-01-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "add_sentiment_fields"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns to sentiment_results table
    op.add_column("sentiment_results", sa.Column("delivery_risk", sa.String(20), server_default="unknown", nullable=False))
    op.add_column("sentiment_results", sa.Column("team_morale", sa.String(20), server_default="unknown", nullable=False))
    op.add_column("sentiment_results", sa.Column("burnout_probability", sa.Float, server_default="0.0", nullable=False))
    op.add_column("sentiment_results", sa.Column("timeline_signals", postgresql.JSON(astext_type=sa.Text()), server_default="[]", nullable=True))
    op.add_column("sentiment_results", sa.Column("blockers", postgresql.JSON(astext_type=sa.Text()), server_default="[]", nullable=True))
    op.add_column("sentiment_results", sa.Column("conflicts", postgresql.JSON(astext_type=sa.Text()), server_default="[]", nullable=True))


def downgrade() -> None:
    op.drop_column("sentiment_results", "conflicts")
    op.drop_column("sentiment_results", "blockers")
    op.drop_column("sentiment_results", "timeline_signals")
    op.drop_column("sentiment_results", "burnout_probability")
    op.drop_column("sentiment_results", "team_morale")
    op.drop_column("sentiment_results", "delivery_risk")