import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base

if TYPE_CHECKING:
    from backend.models.account import Account


class Platform(Base):
    __tablename__ = "platforms"

    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
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
    icon: Mapped[str] = mapped_column(
        String,
        nullable=True,
    )
    accounts: Mapped[list["Account"]] = relationship(
        "Account",
        back_populates="platform",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Platform {self.platform_name}>"