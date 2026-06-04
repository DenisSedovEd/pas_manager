import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base

if TYPE_CHECKING:
    from backend.models.account import Account


class CategoryTable(Base):
    __tablename__ = "categories"

    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False,
    )
    category_name: Mapped[str] = mapped_column(
        String,
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
    order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    parent_id: Mapped[Optional[str]] = mapped_column(
        Text,
        ForeignKey("categories.id"),
        nullable=True,
        default=None,
    )
    parent: Mapped[Optional["CategoryTable"]] = relationship(
        "CategoryTable",
        remote_side="CategoryTable.id",
        back_populates="children",
        lazy="select",
    )
    children: Mapped[list["CategoryTable"]] = relationship(
        "CategoryTable",
        back_populates="parent",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    accounts: Mapped[list["Account"]] = relationship(
        "Account",
        back_populates="category",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Category {self.category_name}>"
