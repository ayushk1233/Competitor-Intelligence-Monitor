"""seed default organization

Revision ID: 9c18bf49cd0c
Revises: b340921b175b
Create Date: 2026-06-23
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid


revision = "9c18bf49cd0c"
down_revision = "b340921b175b"
branch_labels = None
depends_on = None


DEFAULT_ORG_ID = uuid.UUID(
    "00000000-0000-0000-0000-000000000001"
)


def upgrade():

    op.execute(
        sa.text(
            """
            INSERT INTO organizations (
                id,
                name,
                slug,
                is_active
            )
            VALUES (
                :id,
                'Default Organization',
                'default-org',
                true
            )
            ON CONFLICT (slug)
            DO NOTHING
            """
        ).bindparams(id=str(DEFAULT_ORG_ID))
    )

    op.execute(
        sa.text(
            """
            UPDATE users
            SET organization_id = :org_id
            WHERE organization_id IS NULL
            """
        ).bindparams(org_id=str(DEFAULT_ORG_ID))
    )


def downgrade():

    op.execute(
        sa.text(
            """
            UPDATE users
            SET organization_id = NULL
            WHERE organization_id = :org_id
            """
        ).bindparams(org_id=str(DEFAULT_ORG_ID))
    )

    op.execute(
        sa.text(
            """
            DELETE FROM organizations
            WHERE id = :org_id
            """
        ).bindparams(org_id=str(DEFAULT_ORG_ID))
    )
