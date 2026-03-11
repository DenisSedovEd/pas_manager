from fastapi import APIRouter, Header, Depends, HTTPException

from backend.core.security import verify_telegram_data
from backend.core.session import session_manager
from backend.dependencies import get_platform_service
from backend.schemas.platform import PlatformResponseSchema, PlatformRequestSchema
from backend.services.platform_service import PlatformService

router = APIRouter(prefix="/platform")


@router.get("/list")
async def get_platforms(
        authorization: str = Header(...),
        service: PlatformService = Depends(get_platform_service),
) -> list[PlatformResponseSchema]:
    """GET /pas-manager/v1/platform/list"""
    user = verify_telegram_data(authorization)

    if not session_manager.is_active(user["id"]):
        raise HTTPException(status_code=401, detail="Locker is closed")

    platforms = await service.get_platforms()
    return platforms


@router.get("/{platform_id}")
async def get_platform(
        platform_id: str,
        authorization: str = Header(...),
        service: PlatformService = Depends(get_platform_service),
) -> PlatformResponseSchema:
    """GET /pas-manager/v1/platform/{platform_id}"""
    user = verify_telegram_data(authorization)

    if not session_manager.is_active(user["id"]):
        raise HTTPException(status_code=401, detail="Locker is closed")

    platform = await service.get_platform(platform_id)
    return platform


@router.post("")
async def add_platform(
        payload: PlatformRequestSchema,
        authorization: str = Header(...),
        service: PlatformService = Depends(get_platform_service),
) -> PlatformResponseSchema:
    """POST /pas-manager/v1/platform"""
    user = verify_telegram_data(authorization)

    if not session_manager.is_active(user["id"]):
        raise HTTPException(status_code=401, detail="Locker is closed")

    new_platform = await service.add_platform(payload)
    return new_platform


@router.put("/{platform_id}")
async def update_platform(
        platform_id: str,
        payload: PlatformRequestSchema,
        authorization: str = Header(...),
        service: PlatformService = Depends(get_platform_service),
) -> PlatformResponseSchema:
    """PUT /pas-manager/v1/platform/{platform_id}"""
    user = verify_telegram_data(authorization)

    if not session_manager.is_active(user["id"]):
        raise HTTPException(status_code=401, detail="Locker is closed")

    platform = await service.update_platform(platform_id, payload)
    return platform


@router.delete("/{platform_id}")
async def delete_platform(
    platform_id: str,
    transfer: bool = True, # Параметр из Query string
    authorization: str = Header(...),
    service: PlatformService = Depends(get_platform_service),
):
    verify_telegram_data(authorization)
    try:
        await service.delete_platform(platform_id, transfer_accounts=transfer)
        return {"status": "success"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))