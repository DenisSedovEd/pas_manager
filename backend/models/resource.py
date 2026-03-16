import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Text, String
from sqlalchemy.orm import mapped_column, Mapped, relationship

from backend.models.base import Base

if TYPE_CHECKING:
    from backend.models.account import Account


class ResourceTable(Base):
    __tablename__ = "resources"

    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False,
    )
    resource_name: Mapped[str] = mapped_column(
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
        back_populates="resource",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
