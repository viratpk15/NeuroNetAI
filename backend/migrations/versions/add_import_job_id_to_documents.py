"""Add import_job_id to documents table

Revision ID: add_import_job_id_to_documents
Revises: add_sentiment_fields
Create Date: 2024-01-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "add_import_job_id_to_documents"
down_revision = "add_sentiment_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add import_job_id column to documents table
    op.add_column("documents", sa.Column("import_job_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key("documents_import_job_id_fkey", "documents", "import_jobs", ["import_job_id"], ["id"])


def downgrade() -> None:
    op.drop_constraint("documents_import_job_id_fkey", "documents", type_="foreignkey")
    op.drop_column("documents", "import_job_id")