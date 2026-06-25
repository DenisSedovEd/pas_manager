from fastapi import APIRouter, Depends, HTTPException

from backend.core.session import session_manager
from backend.dependencies import get_current_user, get_resource_service
from backend.schemas.resource_schema import (
    ResourceResponseSchema,
    ResourceRequestSchema,
)
from backend.schemas.response_schema import SuccessResponse
from backend.services.resource_service import ResourceService

router = APIRouter(prefix="/resource")


@router.get("/list")
async def get_resources(
    user: dict = Depends(get_current_user),
    service: ResourceService = Depends(get_resource_service),
) -> list[ResourceResponseSchema]:

    if not session_manager.is_active(user["id"], user["session_kind"]):
        raise HTTPException(status_code=401, detail="Locker is closed")

    resources = await service.get_resources()
    return resources


@router.get("/by-name/{resource_name}", response_model=ResourceResponseSchema)
async def get_resource_by_name(
    resource_name: str,
    user: dict = Depends(get_current_user),
    service: ResourceService = Depends(get_resource_service),
) -> ResourceResponseSchema:
    if not session_manager.is_active(user["id"], user["session_kind"]):
        raise HTTPException(status_code=401, detail="Locker is closed")
    return await service.get_by_name(resource_name)


@router.post("", response_model=ResourceResponseSchema)
async def create_resource(
    payload: ResourceRequestSchema,
    user: dict = Depends(get_current_user),
    service: ResourceService = Depends(get_resource_service),
) -> ResourceResponseSchema:

    if not session_manager.is_active(user["id"], user["session_kind"]):
        raise HTTPException(status_code=401, detail="Locker is closed")

    new_resource = await service.add_resource(payload)
    return new_resource


@router.get("/{resource_id}")
async def get_resource(
    resource_id: str,
    user: dict = Depends(get_current_user),
    service: ResourceService = Depends(get_resource_service),
) -> ResourceResponseSchema:

    if not session_manager.is_active(user["id"], user["session_kind"]):
        raise HTTPException(status_code=401, detail="Locker is closed")

    resource = await service.get_resource(resource_id)
    return resource
