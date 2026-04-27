from fastapi import APIRouter, Depends, HTTPException

from backend.core.config import settings as app_settings
from backend.core.security import MasterPasswordService
from backend.core.session import session_manager
from backend.dependencies import get_current_user, get_db_repo
from backend.models import AppSettings
from backend.repositories import DatabaseRepository
from backend.schemas.main_router_schema import StatusResponse, UnlockRequest
from backend.schemas.response_schema import SuccessResponse

router = APIRouter(prefix="/web")


@router.post("/auth/unlock")
async def web_unlock(
    payload: UnlockRequest,
    db_repo: DatabaseRepository = Depends(get_db_repo),
) -> dict:
    """Разблокировка браузерной сессии по мастер-паролю, без TG initData."""
    settings = await db_repo.get(AppSettings, filters={"id": app_settings.app.admin_id})

    if not settings:
        raise HTTPException(
            status_code=500, detail="Application settings not initialized"
        )

    if not MasterPasswordService().verify_password(
        payload.master_password, settings.master_password_hash
    ):
        raise HTTPException(status_code=403, detail="Wrong password")

    token = session_manager.create_browser_session(
        app_settings.tg.user_id, payload.master_password
    )
    return {"token": token}


@router.get("/auth/status")
async def web_status(user: dict = Depends(get_current_user)) -> StatusResponse:
    """Проверка валидности Bearer-токена."""
    return StatusResponse(
        user_id=user["id"], is_unlocked=session_manager.is_active(user["id"])
    )


@router.post("/auth/logout")
async def web_logout(user: dict = Depends(get_current_user)) -> SuccessResponse:
    """Завершение браузерной сессии."""
    session_manager.close_session(user["id"])
    return SuccessResponse()
