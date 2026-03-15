"""rename-fields

Revision ID: c085f009d3bf
Revises: ac215dab4ae6
Create Date: 2026-03-15 15:57:02.533739

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c085f009d3bf"
down_revision: Union[str, Sequence[str], None] = "ac215dab4ae6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("accounts", schema=None) as batch_op:
        # 1. Добавляем новые колонки с nullable=True (временно)
        batch_op.add_column(sa.Column("login", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("label", sa.String(), nullable=True))

    # 2. Копируем данные
    op.execute("UPDATE accounts SET login = user_name")
    op.execute("UPDATE accounts SET label = tags")

    # 3. Меняем login на NOT NULL (label остаётся nullable)
    with op.batch_alter_table("accounts", schema=None) as batch_op:
        batch_op.alter_column("login", nullable=False)
        batch_op.drop_column("tags")
        batch_op.drop_column("user_name")


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("accounts", schema=None) as batch_op:
        batch_op.add_column(sa.Column("user_name", sa.String(), nullable=False))
        batch_op.add_column(sa.Column("tags", sa.String(), nullable=True))

    op.execute("UPDATE accounts SET user_name = login")
    op.execute("UPDATE accounts SET tags = label")

    with op.batch_alter_table("accounts", schema=None) as batch_op:
        batch_op.drop_column("login")
        batch_op.drop_column("label")
