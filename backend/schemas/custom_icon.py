from datetime import datetime

from pydantic import BaseModel, Field


class CustomIconResponseSchema(BaseModel):
    """Метаданные пользовательской иконки."""

    id: str
    key: str = Field(description="Значение для category.icon, например custom:{id}")
    label: str | None = None
    content_type: str
    fallback_emoji: str = "📁"
    created_at: datetime
