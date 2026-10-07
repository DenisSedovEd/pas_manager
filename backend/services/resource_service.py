import uuid

from sqlalchemy import and_, delete, update

from backend.models.account import Account
from backend.models.custom_field import CustomFieldValueTable
from backend.models.resource import ResourceTable
from backend.repositories import DatabaseRepository
from backend.schemas.resource_schema import (
    ResourceResponseSchema,
    ResourceRequestSchema,
)

DEFAULT_RESOURCE_NAME = "Без площадки"


class ResourceService:
    """CRUD площадок (ресурсов)."""

    def __init__(self, db_repo: DatabaseRepository):
        self.db_repo = db_repo

    def _to_schema(self, resource: ResourceTable) -> ResourceResponseSchema:
        return ResourceResponseSchema(
            id=resource.id,
            resource_name=resource.resource_name,
            description=resource.description,
            icon=resource.icon,
        )

    async def get_resource(self, resource_id: str) -> ResourceResponseSchema:
        """Площадка по id."""
        resource = await self.db_repo.get(
            ResourceTable,
            filters={"id": resource_id},
        )

        if not resource:
            raise ValueError(f"Resource with id {resource_id} not found")

        return self._to_schema(resource)

    async def get_by_name(self, resource_name: str) -> ResourceResponseSchema:
        """Площадка по имени."""
        resource = await self.db_repo.get(
            ResourceTable,
            filters={"resource_name": resource_name},
        )
        if not resource:
            raise ValueError(f"Resource with name {resource_name} not found")
        return self._to_schema(resource)

    async def get_resources(self) -> list[ResourceResponseSchema]:
        """Список всех площадок."""
        resources = await self.db_repo.get_list(ResourceTable)
        return [self._to_schema(res) for res in resources]

    async def add_resource(
        self, resource: ResourceRequestSchema
    ) -> ResourceResponseSchema:
        """Создать площадку."""
        new_id = str(uuid.uuid4())
        new_resource = ResourceTable(
            id=new_id,
            resource_name=resource.resource_name,
            description=resource.description,
            icon=resource.icon,
        )
        await self.db_repo.add(new_resource)
        return self._to_schema(new_resource)

    async def update_resource(
        self, resource_id: str, data: ResourceRequestSchema
    ) -> ResourceResponseSchema:
        """Обновить площадку; привязки аккаунтов по id не меняются."""
        resource = await self.db_repo.get(
            ResourceTable,
            filters={"id": resource_id},
        )
        if not resource:
            raise ValueError(f"Resource with id {resource_id} not found")

        name = data.resource_name.strip()
        if not name:
            raise ValueError("Resource name is required")

        duplicate = await self.db_repo.get(
            ResourceTable,
            filters={"resource_name": name},
        )
        if duplicate and duplicate.id != resource_id:
            raise ValueError("Resource with this name already exists")

        await self.db_repo.update(
            ResourceTable,
            filters={"id": resource_id},
            values={
                "resource_name": name,
                "description": data.description,
                "icon": data.icon,
            },
        )

        return ResourceResponseSchema(
            id=resource_id,
            resource_name=name,
            description=data.description,
            icon=data.icon,
        )

    async def _get_or_create_default(self) -> ResourceTable:
        """Системная площадка для аккаунтов без явной привязки."""
        default = await self.db_repo.get(
            ResourceTable,
            filters={"resource_name": DEFAULT_RESOURCE_NAME},
        )
        if default:
            return default
        default = ResourceTable(
            id=str(uuid.uuid4()),
            resource_name=DEFAULT_RESOURCE_NAME,
            description="По умолчанию",
            icon=None,
        )
        await self.db_repo.add(default)
        return default

    async def delete_resource(self, resource_id: str) -> None:
        """Удалить площадку; аккаунты переносятся на «Без площадки»."""
        resource = await self.db_repo.get(
            ResourceTable,
            filters={"id": resource_id},
        )
        if not resource:
            raise ValueError(f"Resource with id {resource_id} not found")

        if resource.resource_name == DEFAULT_RESOURCE_NAME:
            raise ValueError("Нельзя удалить системную площадку «Без площадки»")

        default = await self._get_or_create_default()
        if default.id == resource_id:
            raise ValueError("Нельзя удалить системную площадку «Без площадки»")

        session = self.db_repo.session
        await session.execute(
            update(Account)
            .where(Account.resource_id == resource_id)
            .values(resource_id=default.id)
        )
        await session.execute(
            delete(CustomFieldValueTable).where(
                and_(
                    CustomFieldValueTable.entity_type == "resource",
                    CustomFieldValueTable.entity_id == resource_id,
                )
            )
        )
        # SQL-delete, чтобы cascade ORM не затронул аккаунты в сессии
        await session.execute(
            delete(ResourceTable).where(ResourceTable.id == resource_id)
        )
        await session.commit()
        await session.expire_all()
