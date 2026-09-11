"""fix-accounts-id-sequence

Revision ID: e4f5a6b7c8d9
Revises: d1e2f3a4b5c6
Create Date: 2026-09-11 16:15:00.000000

"""

from typing import Sequence, Union

from alembic import op

revision: str = "e4f5a6b7c8d9"
down_revision: Union[str, Sequence[str], None] = "d1e2f3a4b5c6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Добавить sequence для accounts.id, если её нет."""
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = current_schema()
                  AND table_name = 'accounts'
                  AND column_name = 'id'
                  AND column_default IS NULL
                  AND is_identity = 'NO'
            ) THEN
                CREATE SEQUENCE IF NOT EXISTS accounts_id_seq AS integer;
                PERFORM setval(
                    'accounts_id_seq',
                    GREATEST(
                        COALESCE((SELECT MAX(id) FROM accounts), 0),
                        0
                    ) + 1,
                    false
                );
                ALTER TABLE accounts
                    ALTER COLUMN id SET DEFAULT nextval('accounts_id_seq');
                ALTER SEQUENCE accounts_id_seq OWNED BY accounts.id;
            END IF;
        END $$;
        """
    )


def downgrade() -> None:
    """Убрать sequence default у accounts.id."""
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_schema = current_schema()
                  AND table_name = 'accounts'
                  AND column_name = 'id'
                  AND column_default LIKE 'nextval(%accounts_id_seq%'
            ) THEN
                ALTER TABLE accounts ALTER COLUMN id DROP DEFAULT;
                DROP SEQUENCE IF EXISTS accounts_id_seq;
            END IF;
        END $$;
        """
    )
