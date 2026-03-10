from sqlalchemy.orm import selectinload

from src.models.platform import Platform
from src.repositories import DatabaseRepository
from src.schemas.platform import PlatformResponseSchema, PlatformRequestSchema
import uuid


class PlatformService:
    def __init__(self, db_repo: DatabaseRepository):
        self.db_repo = db_repo

    async def get_platforms(self):
        # Используем selectinload, чтобы избежать MissingGreenlet
        return await self.db_repo.get_list(
            Platform,
            options=[selectinload(Platform.accounts)]
        )

    async def add_platform(self, payload: PlatformRequestSchema):
        # Создаем объект модели из схемы
        new_platform = Platform(
            platform_name=payload.name,
            description=str(payload.description),
        )
        await self.db_repo.add(new_platform)

        # После добавления нужно подгрузить пустой список аккаунтов,
        # чтобы accounts_count (свойство модели) не выдало ошибку
        return await self.db_repo.get(Platform, filters={"id": new_platform.id})