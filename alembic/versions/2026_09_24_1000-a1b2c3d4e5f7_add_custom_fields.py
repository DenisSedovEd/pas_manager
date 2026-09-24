"""add-custom-fields

Revision ID: a1b2c3d4e5f7
Revises: e4f5a6b7c8d9
Create Date: 2026-09-24 10:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f7"
down_revision: Union[str, Sequence[str], None] = "e4f5a6b7c8d9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Создать таблицы кастомных полей."""
    op.create_table(
        "custom_fields",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("is_required", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_secret", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_table(
        "custom_field_values",
        sa.Column("id", sa.Text(), nullable=False),
        sa.Column("field_id", sa.Text(), nullable=False),
        sa.Column("entity_type", sa.String(), nullable=False),
        sa.Column("entity_id", sa.Text(), nullable=False),
        sa.Column("value", sa.Text(), nullable=True),
        sa.Column("encrypted_data", sa.String(), nullable=True),
        sa.Column("salt", sa.String(), nullable=True),
        sa.Column("nonce", sa.String(), nullable=True),
        sa.ForeignKeyConstraint(
            ["field_id"],
            ["custom_fields.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "field_id",
            "entity_type",
            "entity_id",
            name="uq_custom_field_value_entity",
        ),
    )
    op.create_index(
        "ix_custom_field_values_entity",
        "custom_field_values",
        ["entity_type", "entity_id"],
    )


def downgrade() -> None:
    """Удалить таблицы кастомных полей."""
    op.drop_index("ix_custom_field_values_entity", table_name="custom_field_values")
    op.drop_table("custom_field_values")
    op.drop_table("custom_fields")
