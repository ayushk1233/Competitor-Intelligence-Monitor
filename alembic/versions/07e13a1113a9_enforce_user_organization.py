"""enforce user organization

Revision ID: 07e13a1113a9
Revises: 9c18bf49cd0c
Create Date: 2026-06-23
"""

from alembic import op
import sqlalchemy as sa


revision = "07e13a1113a9"
down_revision = "9c18bf49cd0c"
branch_labels = None
depends_on = None


def upgrade():

    op.alter_column(
        "users",
        "organization_id",
        existing_type=sa.UUID(),
        nullable=False,
    )


def downgrade():

    op.alter_column(
        "users",
        "organization_id",
        existing_type=sa.UUID(),
        nullable=True,
    )
