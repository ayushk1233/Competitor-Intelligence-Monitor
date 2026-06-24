"""enable pgvector validation

Revision ID: ce7b1c51b293
Revises: 07e13a1113a9
"""

from alembic import op


revision = "ce7b1c51b293"
down_revision = "07e13a1113a9"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade():
    op.execute("DROP EXTENSION IF EXISTS vector")
