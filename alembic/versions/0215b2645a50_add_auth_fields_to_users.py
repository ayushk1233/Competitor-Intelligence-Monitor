"""add_auth_fields_to_users

Revision ID: 0215b2645a50
Revises: 5de7c8d6acf9
Create Date: 2026-06-09 17:13:33.512833

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0215b2645a50'
down_revision: Union[str, None] = '5de7c8d6acf9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "password_hash",
            sa.String(length=255),
            nullable=True,
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "last_login_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "users",
        "last_login_at",
    )

    op.drop_column(
        "users",
        "password_hash",
    )
