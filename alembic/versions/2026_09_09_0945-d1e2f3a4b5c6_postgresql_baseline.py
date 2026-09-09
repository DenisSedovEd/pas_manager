"""postgresql-baseline

Revision ID: d1e2f3a4b5c6
Revises:
Create Date: 2026-09-09 09:45:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d1e2f3a4b5c6"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Создать актуальную схему для PostgreSQL."""
    op.create_table(
        "categories",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("category_name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("icon", sa.String(), nullable=True),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("parent_id", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["categories.id"],
            name=op.f("fk_categories_parent_id_categories"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_categories")),
    )
    op.create_table(
        "resources",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("resource_name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("icon", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_resources")),
        sa.UniqueConstraint(
            "resource_name",
            name=op.f("uq_resources_resource_name"),
        ),
    )
    op.create_table(
        "app_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("master_password_hash", sa.String(), nullable=False),
        sa.Column("encrypted_master_password", sa.String(), nullable=True),
        sa.Column("bio_enc_data", sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_app_settings")),
    )
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
    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("category_id", sa.Text(), nullable=False),
        sa.Column("resource_id", sa.Text(), nullable=True),
        sa.Column("login", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(), nullable=True),
        sa.Column("encrypted_data", sa.String(), nullable=False),
        sa.Column("salt", sa.String(), nullable=False),
        sa.Column("nonce", sa.String(), nullable=False),
        sa.Column("tag", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["categories.id"],
            name=op.f("fk_accounts_category_id_categories"),
        ),
        sa.ForeignKeyConstraint(
            ["resource_id"],
            ["resources.id"],
            name=op.f("fk_accounts_resource_id_resources"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_accounts")),
    )


def downgrade() -> None:
    """Удалить схему."""
    op.drop_table("accounts")
    op.drop_table("custom_icons")
    op.drop_table("app_settings")
    op.drop_table("resources")
    op.drop_table("categories")
