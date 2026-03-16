import uuid

from backend.models.resource import ResourceTable
from backend.repositories import DatabaseRepository
from backend.schemas.resource_schema import (
    ResourceResponseSchema,
    ResourceRequestSchema,
)


class ResourceService:
    def __init__(self, db_repo: DatabaseRepository):
        self.db_repo = db_repo

    async def get_resource(self, resource_id: str) -> ResourceResponseSchema:
        resource = await self.db_repo.get(
            ResourceTable,
            filters={"id": resource_id},
        )

        if not resource:
            raise ValueError(f"Resource with id {resource_id} not found")

        return ResourceResponseSchema(
            id=resource.id,
            resource_name=resource.resource_name,
            description=resource.description,
            icon=resource.icon,
        )

    async def get_by_name(self, resource_name: str) -> ResourceResponseSchema:
        resource = await self.db_repo.get(
            ResourceTable,
            filters={"resource_name": resource_name},
        )
        return ResourceResponseSchema(
            id=resource.id,
            resource_name=resource.resource_name,
            description=resource.description,
            icon=resource.icon,
        )

    async def get_resources(self) -> list[ResourceResponseSchema]:
        resources = await self.db_repo.get_list(ResourceTable)
        result = [
            ResourceResponseSchema(
                id=res.id,
                resource_name=res.resource_name,
                description=res.description,
                icon=res.icon,
            )
            for res in resources
        ]
        return result

    async def add_resource(
        self, resource: ResourceRequestSchema
    ) -> ResourceResponseSchema:
        new_id = str(uuid.uuid4())
        new_resource = ResourceTable(
            id=new_id,
            resource_name=resource.resource_name,
            description=resource.description,
            icon=resource.icon,
        )
        await self.db_repo.add(new_resource)

        return ResourceResponseSchema(
            id=new_resource.id,
            resource_name=new_resource.resource_name,
            description=new_resource.description,
            icon=new_resource.icon,
        )
