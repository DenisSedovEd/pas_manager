"""add-hash-settings

Revision ID: bf901f29234e
Revises: dcba73fec760
Create Date: 2026-03-11 09:52:38.059444

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "bf901f29234e"
down_revision: Union[str, Sequence[str], None] = "dcba73fec760"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    master_hash = "$argon2id$v=19$m=65536,t=3,p=4$PXKTmYu3NN+u00mparsDvA$MtiTYZGpig8EHgD06f211002/azC9gu0n5nw6kI9Vdg"

    # Вставляем запись с фиксированным id=1, чтобы ручка /unlock всегда её находила
    op.execute(
        sa.text(
            "INSERT INTO app_settings (id, master_password_hash) VALUES (1, :hash)"
        ).bindparams(hash=master_hash)
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(sa.text("DELETE FROM app_settings WHERE id = 1"))
    # ### end Alembic commands ###
