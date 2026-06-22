"""add organizations foundation

Revision ID: b340921b175b
Revises: 0215b2645a50
Create Date: 2026-06-22

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "b340921b175b"
down_revision = "0215b2645a50"
branch_labels = None
depends_on = None


def upgrade():

    op.create_table(
        "organizations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "slug",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug"),
    )

    op.create_index(
        "ix_organizations_slug",
        "organizations",
        ["slug"],
        unique=False,
    )

    op.add_column(
        "users",
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )

    op.create_index(
        op.f("ix_users_organization_id"),
        "users",
        ["organization_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_users_organization_id",
        "users",
        "organizations",
        ["organization_id"],
        ["id"],
    )


def downgrade():

    op.drop_constraint(
        "fk_users_organization_id",
        "users",
        type_="foreignkey",
    )

    op.drop_index(
        op.f("ix_users_organization_id"),
        table_name="users",
    )

    op.drop_column(
        "users",
        "organization_id",
    )

    op.drop_index(
        "ix_organizations_slug",
        table_name="organizations",
    )

    op.drop_table("organizations")
