"""add-custom-icons-table

Revision ID: c7f8e9d0a1b2
Revises: a1b2c3d4e5f6
Create Date: 2026-08-10 20:30:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "c7f8e9d0a1b2"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "custom_icons",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("label", sa.String(), nullable=True),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("content_type", sa.String(), nullable=False),
        sa.Column("fallback_emoji", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_custom_icons")),
    )


def downgrade() -> None:
    op.drop_table("custom_icons")
