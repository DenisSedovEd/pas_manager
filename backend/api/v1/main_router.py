from cryptography.exceptions import InvalidTag
from fastapi import APIRouter, Header, HTTPException, Depends
from pydantic import BaseModel

from backend.core.security import verify_telegram_data, MasterPasswordService
from backend.core.session import session_manager
from backend.dependencies import get_db_repo, get_encrypt_repo
from backend.models import AppSettings
from backend.repositories import DatabaseRepository
from backend.repositories.encryption_repository import EncryptionRepository

router = APIRouter(prefix="/main")


class UnlockRequest(BaseModel):
    master_password: str


class StatusResponse(BaseModel):
    user_id: int
    is_unlocked: bool


class SuccessResponse(BaseModel):
    status: str
    ok: bool


class BiometricRequest(BaseModel):
    bio_token: str


class EnableBiometricRequest(BaseModel):
    encrypted_master_password: str
    bio_enc_data: dict


class LogoutRequest(BaseModel):
    init_data: str


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
        db_repo: DatabaseRepository = Depends(get_db_repo),
) -> SuccessResponse:
    """Разблокировка с мастер-паролем"""
    secure = MasterPasswordService()
    user = verify_telegram_data(authorization)

    settings = await db_repo.get(AppSettings, filters={'id': 1})

    if not settings:
        raise HTTPException(status_code=500, detail="Application settings not initialized")

    is_valid = secure.verify_password(
        payload.master_password,
        settings.master_password_hash
    )

    if is_valid:
        session_manager.create_session(user["id"], payload.master_password)
        return SuccessResponse(status="success", ok=True)

    raise HTTPException(status_code=403, detail="Wrong password")


@router.get("/auth/bio-settings")
async def get_bio_settings(
        authorization: str = Header(...),
        db_repo: DatabaseRepository = Depends(get_db_repo),
):
    """Получение настроек биометрии"""
    verify_telegram_data(authorization)
    settings = await db_repo.get(AppSettings, filters={'id': 1})

    if not settings:
        return {"is_enabled": False}

    return {
        "is_enabled": settings.encrypted_master_password is not None,
        "bio_enc_data": settings.bio_enc_data
    }


@router.post("/auth/unlock-biometric")
async def unlock_bio(
        request_data: BiometricRequest,
        authorization: str = Header(...),
        db_repo: DatabaseRepository = Depends(get_db_repo),
        encrypt_repo: EncryptionRepository = Depends(get_encrypt_repo),
) -> SuccessResponse:
    """Разблокировка по FaceID: восстанавливаем мастер-пароль из зашифрованного хранилища"""
    user = verify_telegram_data(authorization)

    settings = await db_repo.get(AppSettings, filters={'id': 1})

    if not settings or not settings.encrypted_master_password or not settings.bio_enc_data:
        raise HTTPException(
            status_code=400,
            detail="Биометрия не настроена. Сначала разблокируйте сейф паролем."
        )

    try:
        recovered_master_password = encrypt_repo.decrypt_data(
            encrypted_data=settings.encrypted_master_password,
            salt=settings.bio_enc_data["salt"],
            nonce=settings.bio_enc_data["nonce"],
            master_password=request_data.bio_token
        )

        session_manager.create_session(user["id"], recovered_master_password)
        return SuccessResponse(status="success", ok=True)

    except (InvalidTag, Exception):
        raise HTTPException(status_code=403, detail="Ошибка биометрической авторизации")


@router.post("/auth/enable-biometric")
async def enable_biometric(
        payload: BiometricRequest,
        authorization: str = Header(...),
        db_repo: DatabaseRepository = Depends(get_db_repo),
        encrypt_repo: EncryptionRepository = Depends(get_encrypt_repo),
) -> SuccessResponse:
    """Включение биометрии: шифруем текущий мастер-пароль из памяти био-токеном"""
    user = verify_telegram_data(authorization)

    if not session_manager.is_active(user["id"]):
        raise HTTPException(status_code=401, detail="Unlock with password first")

    current_master = session_manager.get_master_password(user["id"])

    encryption_result = encrypt_repo.encrypt_data(
        data=current_master,
        master_password=payload.bio_token
    )

    await db_repo.update(
        AppSettings,
        filters={'id': 1},
        values={
            'encrypted_master_password': encryption_result["encrypted_data"],
            'bio_enc_data': {
                "salt": encryption_result["salt"],
                "nonce": encryption_result["nonce"]
            }
        }
    )

    return SuccessResponse(status="biometric_enabled", ok=True)


@router.post("/auth/logout")
async def logout(
        payload: LogoutRequest
) -> dict:
    """Логаут и закрытие сейфа"""
    user = verify_telegram_data(payload.init_data)
    if user and "id" in user:
        session_manager.close_session(user["id"])
        return {"status": "locked", "ok": True}

    return {"status": "error", "ok": False}
