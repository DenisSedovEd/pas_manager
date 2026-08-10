import uuid
from pathlib import Path

from sqlalchemy import select, update

from backend.models.category import CategoryTable
from backend.models.custom_icon import CustomIconTable
from backend.repositories import DatabaseRepository
from backend.schemas.custom_icon import CustomIconResponseSchema

ALLOWED_CONTENT_TYPES: dict[str, str] = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/webp": ".webp",
    "image/svg+xml": ".svg",
}
MAX_ICON_BYTES = 512 * 1024
ICONS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "category_icons"
DEFAULT_FALLBACK = "📁"


class CustomIconService:
    """CRUD пользовательских иконок категорий."""

    def __init__(self, db_repo: DatabaseRepository):
        self.db_repo = db_repo

    def _to_schema(self, icon: CustomIconTable) -> CustomIconResponseSchema:
        return CustomIconResponseSchema(
            id=icon.id,
            key=f"custom:{icon.id}",
            label=icon.label,
            content_type=icon.content_type,
            fallback_emoji=icon.fallback_emoji,
            created_at=icon.created_at,
        )

    def _ensure_dir(self) -> None:
        ICONS_DIR.mkdir(parents=True, exist_ok=True)

    def _path_for(self, icon: CustomIconTable) -> Path:
        return ICONS_DIR / icon.filename

    async def list_icons(self) -> list[CustomIconResponseSchema]:
        """Список загруженных иконок."""
        result = await self.db_repo.session.execute(
            select(CustomIconTable).order_by(CustomIconTable.created_at.desc())
        )
        icons = result.scalars().all()
        return [self._to_schema(icon) for icon in icons]

    async def get_icon(self, icon_id: str) -> CustomIconTable:
        """Получить запись иконки или ошибка."""
        icon = await self.db_repo.get(CustomIconTable, filters={"id": icon_id})
        if not icon:
            raise ValueError(f"Custom icon {icon_id} not found")
        return icon

    async def get_file(self, icon_id: str) -> tuple[Path, str]:
        """Путь к файлу и content-type."""
        icon = await self.get_icon(icon_id)
        path = self._path_for(icon)
        if not path.is_file():
            raise ValueError(f"Custom icon file {icon_id} missing")
        return path, icon.content_type

    async def create_icon(
        self,
        data: bytes,
        content_type: str,
        label: str | None = None,
        fallback_emoji: str = DEFAULT_FALLBACK,
    ) -> CustomIconResponseSchema:
        """Сохранить загруженный файл иконки."""
        if content_type not in ALLOWED_CONTENT_TYPES:
            raise ValueError("Unsupported image type")
        if len(data) == 0:
            raise ValueError("Empty file")
        if len(data) > MAX_ICON_BYTES:
            raise ValueError("File too large (max 512 KB)")

        self._ensure_dir()
        icon_id = str(uuid.uuid4())
        ext = ALLOWED_CONTENT_TYPES[content_type]
        filename = f"{icon_id}{ext}"
        path = ICONS_DIR / filename
        path.write_bytes(data)

        icon = CustomIconTable(
            id=icon_id,
            label=label,
            filename=filename,
            content_type=content_type,
            fallback_emoji=fallback_emoji or DEFAULT_FALLBACK,
        )
        await self.db_repo.add(icon)
        return self._to_schema(icon)

    async def delete_icon(self, icon_id: str) -> None:
        """Удалить иконку и заменить её в категориях на fallback."""
        icon = await self.get_icon(icon_id)
        fallback = icon.fallback_emoji or DEFAULT_FALLBACK
        key = f"custom:{icon_id}"
        path = self._path_for(icon)

        await self.db_repo.session.execute(
            update(CategoryTable)
            .where(CategoryTable.icon == key)
            .values(icon=fallback)
        )
        await self.db_repo.session.delete(icon)
        await self.db_repo.session.commit()
        if path.is_file():
            path.unlink()
