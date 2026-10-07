from fastapi import APIRouter, Depends, HTTPException

from backend.core.session import session_manager
from backend.dependencies import get_current_user, get_resource_service
from backend.schemas.resource_schema import (
    ResourceResponseSchema,
    ResourceRequestSchema,
)
from backend.services.resource_service import ResourceService

router = APIRouter(prefix="/resource")


def _require_open_locker(user: dict) -> None:
    if not session_manager.is_active(user["id"], user["session_kind"]):
        raise HTTPException(status_code=401, detail="Locker is closed")


@router.get("/list")
async def get_resources(
    user: dict = Depends(get_current_user),
    service: ResourceService = Depends(get_resource_service),
) -> list[ResourceResponseSchema]:
    _require_open_locker(user)
    return await service.get_resources()


@router.get("/by-name/{resource_name}", response_model=ResourceResponseSchema)
async def get_resource_by_name(
    resource_name: str,
    user: dict = Depends(get_current_user),
    service: ResourceService = Depends(get_resource_service),
) -> ResourceResponseSchema:
    _require_open_locker(user)
    try:
        return await service.get_by_name(resource_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.post("", response_model=ResourceResponseSchema)
async def create_resource(
    payload: ResourceRequestSchema,
    user: dict = Depends(get_current_user),
    service: ResourceService = Depends(get_resource_service),
) -> ResourceResponseSchema:
    _require_open_locker(user)
    return await service.add_resource(payload)


@router.put("/{resource_id}", response_model=ResourceResponseSchema)
async def update_resource(
    resource_id: str,
    payload: ResourceRequestSchema,
    user: dict = Depends(get_current_user),
    service: ResourceService = Depends(get_resource_service),
) -> ResourceResponseSchema:
    _require_open_locker(user)
    try:
        return await service.update_resource(resource_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/{resource_id}")
async def get_resource(
    resource_id: str,
    user: dict = Depends(get_current_user),
    service: ResourceService = Depends(get_resource_service),
) -> ResourceResponseSchema:
    _require_open_locker(user)
    try:
        return await service.get_resource(resource_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
