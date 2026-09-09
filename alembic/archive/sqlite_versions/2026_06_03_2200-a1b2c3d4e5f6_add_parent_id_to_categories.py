"""add-parent-id-to-categories

Revision ID: a1b2c3d4e5f6
Revises: 3c0e23c7b099
Create Date: 2026-06-03 22:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "3c0e23c7b099"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("PRAGMA foreign_keys=OFF")
    op.execute("""
        CREATE TABLE categories_new (
            id TEXT NOT NULL PRIMARY KEY,
            category_name VARCHAR NOT NULL,
            description VARCHAR,
            icon VARCHAR,
            "order" INTEGER NOT NULL DEFAULT 0,
            parent_id TEXT
        )
    """)
    op.execute("""
        INSERT INTO categories_new (id, category_name, description, icon, "order")
        SELECT id, category_name, description, icon, "order" FROM categories
    """)
    op.drop_table("categories")
    op.execute("ALTER TABLE categories_new RENAME TO categories")
    op.execute("PRAGMA foreign_keys=ON")


def downgrade() -> None:
    op.execute("PRAGMA foreign_keys=OFF")
    op.execute("""
        CREATE TABLE categories_old (
            id TEXT NOT NULL PRIMARY KEY,
            category_name VARCHAR NOT NULL UNIQUE,
            description VARCHAR,
            icon VARCHAR,
            "order" INTEGER NOT NULL DEFAULT 0
        )
    """)
    op.execute("""
        INSERT INTO categories_old (id, category_name, description, icon, "order")
        SELECT id, category_name, description, icon, "order" FROM categories
    """)
    op.drop_table("categories")
    op.execute("ALTER TABLE categories_old RENAME TO categories")
    op.execute("PRAGMA foreign_keys=ON")
