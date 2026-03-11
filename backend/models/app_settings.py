from sqlalchemy import Integer, String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from backend.models.base import Base


class AppSettings(Base):
    __tablename__ = "app_settings"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    master_password_hash: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    encrypted_master_password: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )
    bio_enc_data: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )