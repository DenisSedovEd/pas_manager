import uuid
from sqlalchemy import Integer, String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.platform import Platform
from src.models.base import Base


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    platform_id: Mapped[str] = mapped_column(  # ← Строка для SQLite
        Text,  # ← SQLite хранит как TEXT
        ForeignKey("platforms.id"),
        nullable=False,
    )
    platform: Mapped["Platform"] = relationship(
        "Platform",
        back_populates="accounts",
    )
    user_name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    email: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )
    phone: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )
    tags: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    # Encryption fields
    encrypted_data: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    salt: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    nonce: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    tag: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Account {self.user_name}@{self.platform_id}>"