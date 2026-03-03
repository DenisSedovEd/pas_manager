import uuid

from sqlalchemy import Integer, String, ForeignKey, UUID
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
    platform_id: Mapped[uuid.UUID] = mapped_column(
        UUID,
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

    # crypto
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
