from cryptography.exceptions import InvalidTag
from fastapi import APIRouter, HTTPException, Depends

from backend.core.security import MasterPasswordService
from backend.core.config import settings as app_settings
from backend.core.session import session_manager
from backend.dependencies import (
    get_db_repo,
    get_encrypt_repo,
    get_current_user,
    get_master_password,
)
from backend.models import AppSettings
from backend.repositories import DatabaseRepository
from backend.repositories.encryption_repository import EncryptionRepository
from backend.schemas.main_router_schema import (
    StatusResponse,
    UnlockRequest,
    BiometricRequest,
)
from backend.schemas.response_schema import SuccessResponse

router = APIRouter(prefix="/main")


@router.get("/auth/status")
async def check_status(user: dict = Depends(get_current_user)) -> StatusResponse:
    """Проверка статуса разблокировки"""
    is_unlocked = session_manager.is_active(user["id"])

    return StatusResponse(user_id=user["id"], is_unlocked=is_unlocked)


@router.post("/auth/unlock")
async def unlock(
    payload: UnlockRequest,
    user: dict = Depends(get_current_user),
    db_repo: DatabaseRepository = Depends(get_db_repo),
) -> SuccessResponse:
    """Разблокировка с мастер-паролем"""
    secure = MasterPasswordService()

    settings = await db_repo.get(AppSettings, filters={"id": app_settings.app.admin_id})

    if not settings:
        raise HTTPException(
            status_code=500, detail="Application settings not initialized"
        )

    is_valid = secure.verify_password(
        payload.master_password, settings.master_password_hash
    )
    if is_valid:
        session_manager.create_session(user["id"], payload.master_password)
        return SuccessResponse()

    raise HTTPException(status_code=403, detail="Wrong password")


@router.get("/auth/bio-settings")
async def get_bio_settings(
    user: dict = Depends(get_current_user),
    db_repo: DatabaseRepository = Depends(get_db_repo),
):
    """Получение настроек биометрии"""
    settings = await db_repo.get(AppSettings, filters={"id": app_settings.app.admin_id})

    if not settings.bio_enc_data:
        return {"is_enabled": False}

    return {
        "is_enabled": settings.encrypted_master_password is not None,
        "bio_enc_data": settings.bio_enc_data,
    }


@router.post("/auth/unlock-biometric")
async def unlock_bio(
    request_data: BiometricRequest,
    user: dict = Depends(get_current_user),
    db_repo: DatabaseRepository = Depends(get_db_repo),
    encrypt_repo: EncryptionRepository = Depends(get_encrypt_repo),
) -> SuccessResponse:
    """Разблокировка по FaceID: восстанавливаем мастер-пароль из зашифрованного хранилища"""

    settings = await db_repo.get(AppSettings, filters={"id": app_settings.app.admin_id})

    if (
        not settings
        or not settings.encrypted_master_password
        or not settings.bio_enc_data
    ):
        raise HTTPException(
            status_code=400,
            detail="Биометрия не настроена. Сначала разблокируйте сейф паролем.",
        )

    try:
        recovered_master_password = encrypt_repo.decrypt_data(
            encrypted_data=settings.encrypted_master_password,
            salt=settings.bio_enc_data["salt"],
            nonce=settings.bio_enc_data["nonce"],
            master_password=request_data.bio_token,
        )

        session_manager.create_session(user["id"], recovered_master_password)
        return SuccessResponse()

    except (InvalidTag, Exception):
        raise HTTPException(status_code=403, detail="Ошибка биометрической авторизации")


@router.post("/auth/enable-biometric")
async def enable_biometric(
    payload: BiometricRequest,
    master_password: str = Depends(get_master_password),
    db_repo: DatabaseRepository = Depends(get_db_repo),
    encrypt_repo: EncryptionRepository = Depends(get_encrypt_repo),
) -> SuccessResponse:
    """Включение биометрии: шифруем текущий мастер-пароль из памяти био-токеном"""
    encryption_result = encrypt_repo.encrypt_data(
        data=master_password, master_password=payload.bio_token
    )

    await db_repo.update(
        AppSettings,
        filters={"id": app_settings.app.admin_id},
        values={
            "encrypted_master_password": encryption_result["encrypted_data"],
            "bio_enc_data": {
                "salt": encryption_result["salt"],
                "nonce": encryption_result["nonce"],
            },
        },
    )

    return SuccessResponse()


@router.post("/auth/logout")
async def logout(
    user: dict = Depends(get_current_user),
) -> SuccessResponse:
    """Логаут и закрытие менеджера"""
    session_manager.close_session(user["id"])
    return SuccessResponse()
