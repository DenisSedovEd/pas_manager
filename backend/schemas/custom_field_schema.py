from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator

EntityType = Literal["account", "category", "resource"]


class CustomFieldDefinitionSchema(BaseModel):
    """Определение кастомного поля."""

    id: str
    name: str
    is_required: bool = False
    is_secret: bool = False
    order: int = 0


class CustomFieldCreateSchema(BaseModel):
    """Создание определения поля."""

    name: str = Field(min_length=1)
    is_required: bool = False
    is_secret: bool = False
    order: int = 0


class CustomFieldUpdateSchema(BaseModel):
    """Обновление определения (без смены is_secret)."""

    name: Optional[str] = Field(default=None, min_length=1)
    is_required: Optional[bool] = None
    order: Optional[int] = None


class CustomFieldValueItemSchema(BaseModel):
    """Поле сущности с расшифрованным значением."""

    field_id: str
    name: str
    is_required: bool
    is_secret: bool
    order: int = 0
    value: str = ""


class NewFieldInlineSchema(BaseModel):
    """Новое определение при привязке к сущности."""

    name: str = Field(min_length=1)
    is_required: bool = False
    is_secret: bool = False
    order: int = 0


class CustomFieldValueInputSchema(BaseModel):
    """Элемент атомарной замены значений сущности."""

    field_id: Optional[str] = None
    new_field: Optional[NewFieldInlineSchema] = None
    value: str = ""

    @model_validator(mode="after")
    def require_field_or_new(self) -> "CustomFieldValueInputSchema":
        if not self.field_id and not self.new_field:
            raise ValueError("Укажите field_id или new_field")
        if self.field_id and self.new_field:
            raise ValueError("Укажите либо field_id, либо new_field")
        return self


class CustomFieldValuesReplaceSchema(BaseModel):
    """Тело PUT values для сущности."""

    fields: list[CustomFieldValueInputSchema] = Field(default_factory=list)
