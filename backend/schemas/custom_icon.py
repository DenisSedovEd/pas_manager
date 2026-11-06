from datetime import datetime

from pydantic import BaseModel, Field

from backend.core.shared_config import ICON_FALLBACK_EMOJI


class CustomIconResponseSchema(BaseModel):
    """Метаданные пользовательской иконки."""

    id: str
    key: str = Field(description="Значение для category.icon / resource.icon, например custom:{id}")
    label: str | None = None
    content_type: str
    fallback_emoji: str = ICON_FALLBACK_EMOJI
    created_at: datetime
