import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.ext.hybrid import hybrid_property

from src.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from src.models.account import Account


class Platform(Base):
    __tablename__ = "platforms"

    id: Mapped[uuid.UUID] = mapped_column(
        Text,  # ← SQLite хранит UUID как TEXT
        primary_key=True,
        default=lambda: str(uuid.uuid4()),  # Конвертируем в строку
        nullable=False,
    )
    platform_name: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        String,
        nullable=True,
    )
    accounts: Mapped[list["Account"]] = relationship(
        "Account",
        back_populates="platform",
        lazy="raise",
        cascade="all, delete-orphan",
    )

    @hybrid_property
    def name(self) -> str:
        return self.platform_name

    @hybrid_property
    def icon(self) -> str:
        return "🌐"

    @hybrid_property
    def accounts_count(self) -> int:
        try:
            return len(self.accounts)
        except Exception:
            return 0

    def __repr__(self) -> str:
        return f"<Platform {self.platform_name}>"