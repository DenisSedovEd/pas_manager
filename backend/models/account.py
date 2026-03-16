from sqlalchemy import Integer, String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.category import CategoryTable
from backend.models.resource import ResourceTable
from backend.models.base import Base


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    category_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("categories.id"),
        nullable=False,
    )
    category: Mapped["CategoryTable"] = relationship(
        "CategoryTable",
        back_populates="accounts",
    )
    resource_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("resources.id"),
        nullable=True,
    )
    resource: Mapped["ResourceTable"] = relationship(
        "ResourceTable",
        back_populates="accounts",
    )
    login: Mapped[str] = mapped_column(
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
    order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    label: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )
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
        return f"<Account {self.login}@{self.category_id}>"