from fastapi import APIRouter, Header, Depends, HTTPException

from src.core.security import verify_telegram_data
from src.core.session import session_manager
from src.dependencies import get_platform_service
from src.schemas.platform import PlatformResponseSchema, PlatformRequestSchema
from src.services.platform_service import PlatformService

router = APIRouter(prefix="/platform")


@router.get("/list", response_model=list[PlatformResponseSchema])
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