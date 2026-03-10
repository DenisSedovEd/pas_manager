from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from src.core.security import verify_telegram_data
from src.core.session import session_manager

router = APIRouter(prefix="/main")


class UnlockRequest(BaseModel):
    master_password: str


class StatusResponse(BaseModel):
    user_id: int
    is_unlocked: bool


class SuccessResponse(BaseModel):
    status: str
    ok: bool


@router.get("/auth/status")
async def check_status(authorization: str = Header(...)) -> StatusResponse:
    """Проверка статуса разблокировки"""
    user = verify_telegram_data(authorization)
    is_unlocked = session_manager.is_active(user["id"])

    return StatusResponse(
        user_id=user["id"],
        is_unlocked=is_unlocked
    )


@router.post("/auth/unlock")
async def unlock(
    payload: UnlockRequest,
    authorization: str = Header(...),
) -> SuccessResponse:
    """Разблокировка с мастер-паролем"""
    user = verify_telegram_data(authorization)

    # TODO: Проверить пароль из БД через Argon2
    # Пока хардкод:
    if payload.master_password == "1234":
        session_manager.create_session(user["id"], payload.master_password)
        return SuccessResponse(status="success", ok=True)

    raise HTTPException(status_code=403, detail="Wrong password")


@router.post("/auth/unlock-biometric")
async def unlock_bio(
    bio_token: str = Header(...),
    authorization: str = Header(...),
) -> SuccessResponse:
    """Разблокировка с биометрией"""
    user = verify_telegram_data(authorization)

    # TODO: Проверить bio_token в БД и получить мастер-пароль
    if bio_token:
        # Получаем мастер-пароль из БД по bio_token
        master_password = "1234"  # Заглушка
        session_manager.create_session(user["id"], master_password)
        return SuccessResponse(status="success", ok=True)

    raise HTTPException(status_code=403, detail="Invalid token")


@router.post("/auth/logout")
async def logout(authorization: str = Header(...)) -> dict:
    """Логаут и закрытие сейфа"""
    user = verify_telegram_data(authorization)
    session_manager.close_session(user["id"])
    return {"status": "locked"}