from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Account(Base):
    __tablename__ = "account"
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    service_name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
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
