from src.models import Account
from src.models.platform import Platform
from src.repositories import DatabaseRepository
from src.schemas.platform import PlatformResponseSchema, PlatformRequestSchema
import uuid


class PlatformService:
    def __init__(self, db_repo: DatabaseRepository):
        self.db_repo = db_repo

    async def get_platforms(self) -> list[PlatformResponseSchema]:
        """Получить все платформы с количеством аккаунтов"""
        platforms = await self.db_repo.get_list(Platform)

        result = []
        for platform in platforms:
            # Теперь accounts доступен благодаря lazy="selectin"
            accounts_count = len(platform.accounts) if platform.accounts else 0
            response = PlatformResponseSchema(
                id=platform.id,
                name=platform.platform_name,
                icon=platform.description,
                accounts_count=accounts_count,
            )
            result.append(response)

        return result

    async def get_platform(self, platform_id: str) -> PlatformResponseSchema:
        """Получить одну платформу"""
        platform = await self.db_repo.get(Platform, filters={"id": platform_id})

        if not platform:
            raise ValueError(f"Platform with id {platform_id} not found")

        accounts_count = len(platform.accounts) if platform.accounts else 0
        return PlatformResponseSchema(
            id=platform.id,
            name=platform.platform_name,
            icon=platform.description,
            accounts_count=accounts_count,
        )

    async def add_platform(self, platform_data: PlatformRequestSchema) -> PlatformResponseSchema:
        """Добавить новую платформу"""
        new_id = str(uuid.uuid4())

        new_platform = Platform(
            id=new_id,
            platform_name=platform_data.name,
            description=platform_data.icon,
        )
        await self.db_repo.add(new_platform)

        return PlatformResponseSchema(
            id=new_platform.id,
            name=new_platform.platform_name,
            icon=new_platform.description,
            accounts_count=0,
        )

    async def update_platform(self, platform_id: str, platform_data: PlatformRequestSchema) -> PlatformResponseSchema:
        """Обновить платформу"""
        platform = await self.db_repo.get(Platform, filters={"id": platform_id})

        if not platform:
            raise ValueError(f"Platform with id {platform_id} not found")

        await self.db_repo.update(
            Platform,
            filters={"id": platform_id},
            values={
                "platform_name": platform_data.name,
                "description": platform_data.icon,
            }
        )

        accounts_count = len(platform.accounts) if platform.accounts else 0
        return PlatformResponseSchema(
            id=platform_id,
            name=platform_data.name,
            icon=platform_data.icon,
            accounts_count=accounts_count,
        )

    async def delete_platform(self, platform_id: str, transfer_accounts: bool = True):
        """Удалить платформу с выбором: перенос или удаление аккаунтов"""
        # 1. Ищем удаляемую платформу
        platform = await self.db_repo.get(Platform, filters={"id": platform_id})
        if not platform:
            raise ValueError(f"Platform with id {platform_id} not found")

        if platform.platform_name == "Other":
            raise ValueError("Нельзя удалить системную платформу 'Other'")

        if transfer_accounts:
            # 2. Ищем или создаем платформу Other
            other_platform = await self.db_repo.get(Platform, filters={"platform_name": "Other"})
            if not other_platform:
                other_platform = Platform(
                    platform_name="Other",
                    description="🌐"
                )
                await self.db_repo.add(other_platform)

            # 3. Переносим все аккаунты на 'Other'
            # Используем модель Account напрямую через репозиторий
            from src.models.account import Account
            await self.db_repo.update(
                Account,
                filters={"platform_id": platform_id},
                values={"platform_id": str(other_platform.id)}
            )

        # 4. Удаляем саму платформу
        # Если transfer_accounts=False, сработает cascade="all, delete-orphan" и аккаунты удалятся
        await self.db_repo.delete(platform)