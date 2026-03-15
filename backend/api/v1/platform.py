from fastapi import APIRouter, Depends, HTTPException

from backend.core.session import session_manager
from backend.dependencies import get_platform_service, get_current_user
from backend.schemas.platform import PlatformResponseSchema, PlatformRequestSchema
from backend.schemas.response_schemas import MessageResponse, SuccessResponse
from backend.services.platform_service import PlatformService

router = APIRouter(prefix="/platform")


@router.get("/list")
async def get_platforms(
        user: dict = Depends(get_current_user),
        service: PlatformService = Depends(get_platform_service),
) -> list[PlatformResponseSchema]:
    """GET /pas-manager/v1/platform/list"""

    if not session_manager.is_active(user["id"]):
        raise HTTPException(status_code=401, detail="Locker is closed")

    platforms = await service.get_platforms()
    return platforms


@router.get("/{platform_id}")
async def get_platform(
        platform_id: str,
        user: dict = Depends(get_current_user),
        service: PlatformService = Depends(get_platform_service),
) -> PlatformResponseSchema:
    """GET /pas-manager/v1/platform/{platform_id}"""

    if not session_manager.is_active(user["id"]):
        raise HTTPException(status_code=401, detail="Locker is closed")

    platform = await service.get_platform(platform_id)
    return platform


@router.post("")
async def add_platform(
        payload: PlatformRequestSchema,
        user: dict = Depends(get_current_user),
        service: PlatformService = Depends(get_platform_service),
) -> PlatformResponseSchema:
    """POST /pas-manager/v1/platform"""

    if not session_manager.is_active(user["id"]):
        raise HTTPException(status_code=401, detail="Locker is closed")

    new_platform = await service.add_platform(payload)
    return new_platform


@router.put("/reorder")
async def reorder_platforms(
        payload: list[str],
        user: dict = Depends(get_current_user),
        service: PlatformService = Depends(get_platform_service),
):
    if not session_manager.is_active(user["id"]):
        raise HTTPException(status_code=401, detail="Locker is closed")
    await service.reorder_platforms(payload)
    return SuccessResponse()


@router.put("/{platform_id}")
async def update_platform(
        platform_id: str,
        payload: PlatformRequestSchema,
        user: dict = Depends(get_current_user),
        service: PlatformService = Depends(get_platform_service),
) -> PlatformResponseSchema:
    """PUT /pas-manager/v1/platform/{platform_id}"""

    if not session_manager.is_active(user["id"]):
        raise HTTPException(status_code=401, detail="Locker is closed")

    platform = await service.update_platform(platform_id, payload)
    return platform


@router.delete("/{platform_id}")
async def delete_platform(
        platform_id: str,
        transfer: bool = True,
        user: dict = Depends(get_current_user),
        service: PlatformService = Depends(get_platform_service),
):
    if not session_manager.is_active(user["id"]):
        raise HTTPException(status_code=401, detail="Locker is closed")
    try:
        await service.delete_platform(platform_id, transfer_accounts=transfer)
        return MessageResponse(message='Platform deleted')
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
