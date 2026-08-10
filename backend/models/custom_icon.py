import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.models.base import Base


class CustomIconTable(Base):
    """Пользовательская иконка категории."""

    __tablename__ = "custom_icons"

    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False,
    )
    label: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )
    filename: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    content_type: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    fallback_emoji: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="📁",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    def __repr__(self) -> str:
        return f"<CustomIcon {self.id}>"
