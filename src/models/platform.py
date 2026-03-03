import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Integer, UUID, String

from src.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from src.models.account import Account


class Platform(Base):
    __tablename__ = "platforms"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID,
        primary_key=True,
    )
    description: Mapped[str] = mapped_column(
        String,
    )
    platform_name: Mapped[str] = mapped_column(
        String,
        unique=True,
    )
    accounts: Mapped[list["Account"]] = relationship(
        "Account",
        back_populates="platform",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Service {self.platform_name}>"
