from fastapi import FastAPI, Depends, Header, HTTPException, APIRouter
from pydantic import BaseModel

from src.schemas.bio import BioUnlockRequest
from src.core.security import verify_telegram_data
from src.core.session import session_manager

router = APIRouter(prefix="/main")


class UnlockRequest(BaseModel):
    master_password: str


# Эндпоинт 1: Проверка статуса (нужно ли вводить пароль?)
@router.get("/auth/status")
async def check_status(authorization: str = Header(...)):
    user = verify_telegram_data(authorization)
    is_unlocked = session_manager.is_active(user["id"])

    return {"user_id": user["id"], "is_unlocked": is_unlocked}


# Эндпоинт 2: Разблокировка (Мастер-пароль или эмуляция FaceID)
@router.post("/auth/unlock")
async def unlock(payload: UnlockRequest, authorization: str = Header(...)):
    user = verify_telegram_data(authorization)

    # Тут будет твоя проверка Argon2 из БД. Пока сделаем хардкод:
    if payload.master_password == "1234":
        session_manager.create_session(user["id"])
        return {"status": "success"}

    raise HTTPException(status_code=403, detail="Wrong password")


# Эндпоинт 3: Тот самый "Секретный" функционал
# @router.get("/data/hello")
# async def get_secret_message(authorization: str = Header(...)):
#     user = verify_telegram_data(authorization)
#
#     if not session_manager.is_active(user["id"]):
#         raise HTTPException(status_code=401, detail="Locker is closed")
#
#     return {"message": "Привет, у тебя получилось!"}


@router.post("/auth/unlock-biometric")
async def unlock_bio(payload: BioUnlockRequest, authorization: str = Header(None)):
    user = verify_telegram_data(authorization)

    # В реальной базе мы бы проверили, привязан ли этот bio_token к user_id
    # Для теста просто разрешаем:
    if payload.bio_token:
        session_manager.create_session(user["id"])
        return {"status": "success"}

    raise HTTPException(status_code=403, detail="Invalid token")


@router.post("/auth/logout")
async def logout(authorization: str = Header(...)):
    user = verify_telegram_data(authorization)
    # Используем официальный метод вместо обращения к приватным полям
    session_manager.close_session(user["id"])
    return {"status": "locked"}
