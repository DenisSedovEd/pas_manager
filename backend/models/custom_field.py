import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base

if TYPE_CHECKING:
    pass


class CustomFieldTable(Base):
    """Определение кастомного поля."""

    __tablename__ = "custom_fields"

    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
    )
    is_required: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    is_secret: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )
    values: Mapped[list["CustomFieldValueTable"]] = relationship(
        "CustomFieldValueTable",
        back_populates="field",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<CustomField {self.name}>"


class CustomFieldValueTable(Base):
    """Значение кастомного поля на сущности."""

    __tablename__ = "custom_field_values"
    __table_args__ = (
        UniqueConstraint(
            "field_id",
            "entity_type",
            "entity_id",
            name="uq_custom_field_value_entity",
        ),
    )

    id: Mapped[str] = mapped_column(
        Text,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False,
    )
    field_id: Mapped[str] = mapped_column(
        Text,
        ForeignKey("custom_fields.id", ondelete="CASCADE"),
        nullable=False,
    )
    field: Mapped["CustomFieldTable"] = relationship(
        "CustomFieldTable",
        back_populates="values",
    )
    entity_type: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    entity_id: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    value: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    encrypted_data: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )
    salt: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )
    nonce: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    def __repr__(self) -> str:
        return f"<CustomFieldValue {self.field_id}@{self.entity_type}:{self.entity_id}>"
