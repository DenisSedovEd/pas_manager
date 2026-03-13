from backend.models import Account
from backend.models.platform import Platform
from backend.repositories import DatabaseRepository
from backend.schemas.platform import PlatformResponseSchema, PlatformRequestSchema
import uuid


class PlatformService:
    def __init__(self, db_repo: DatabaseRepository):
        self.db_repo = db_repo

    async def get_platforms(self) -> list[PlatformResponseSchema]:
        platforms = await self.db_repo.get_list(Platform)

        result = []
        for platform in platforms:
            accounts_count = len(platform.accounts) if platform.accounts else 0
            response = PlatformResponseSchema(
                id=platform.id,
                name=platform.platform_name,
                icon=platform.icon,
                description=platform.description,
                order=platform.order,
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
            icon=platform.icon,
            description=platform.description,
            order=platform.order,
            accounts_count=accounts_count,
        )

    async def add_platform(self, platform_data: PlatformRequestSchema) -> PlatformResponseSchema:
        """Добавить новую платформу"""
        new_id = str(uuid.uuid4())

        existing_platforms = await self.db_repo.get_list(Platform)
        new_order = len(existing_platforms)

        new_platform = Platform(
            id=new_id,
            platform_name=platform_data.name,
            icon=platform_data.icon,
            description=platform_data.description,
            order=new_order,
        )
        await self.db_repo.add(new_platform)

        return PlatformResponseSchema(
            id=new_platform.id,
            name=new_platform.platform_name,
            icon=new_platform.icon,
            description=new_platform.description,
            accounts_count=0,
            order=new_platform.order,
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
                'icon': platform_data.icon,
                "description": platform_data.description,
            }
        )

        accounts_count = len(platform.accounts) if platform.accounts else 0
        return PlatformResponseSchema(
            id=platform_id,
            name=platform_data.name,
            icon=platform_data.icon,
            description=platform_data.description,
            accounts_count=accounts_count,
        )

    async def reorder_platforms(self, order_list: list[str]):
        """Пересортируем список платформ"""
        for index, platform_id in enumerate(order_list):
            await self.db_repo.update(
                Platform,
                filters={"id": str(platform_id)},
                values={"order": int(index) },
            )
        return {'status': 'ok'}


    async def delete_platform(self, platform_id: str, transfer_accounts: bool = True):
        """Удалить платформу с выбором: перенос или удаление аккаунтов"""
        platform = await self.db_repo.get(Platform, filters={"id": platform_id})
        if not platform:
            raise ValueError(f"Platform with id {platform_id} not found")

        if platform.platform_name == "Other":
            raise ValueError("Нельзя удалить системную платформу 'Other'")

        if transfer_accounts:
            other_platform = await self.db_repo.get(Platform, filters={"platform_name": "Other"})
            if not other_platform:
                other_platform = Platform(
                    platform_name="Other",
                    description="🌐"
                )
                await self.db_repo.add(other_platform)

            from backend.models.account import Account
            await self.db_repo.update(
                Account,
                filters={"platform_id": platform_id},
                values={"platform_id": str(other_platform.id)}
            )

        await self.db_repo.delete(platform)