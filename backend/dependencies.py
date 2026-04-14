from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db import get_session
from backend.core.security import verify_browser_token, verify_telegram_data
from backend.core.session import session_manager
from backend.repositories import DatabaseRepository
from backend.repositories.encryption_repository import EncryptionRepository
from backend.services.account_service import AccountService
from backend.services.category_service import CategoryService
from backend.services.resource_service import ResourceService


def get_account_service(
    session: AsyncSession = Depends(get_session),
) -> AccountService:
    db_repo = DatabaseRepository(session)
    encrypt_repo = EncryptionRepository()
    return AccountService(db_repo, encrypt_repo)


def get_category_service(
    session: AsyncSession = Depends(get_session),
) -> CategoryService:
    db_repo = DatabaseRepository(session)
    return CategoryService(db_repo)


def get_resource_service(
    session: AsyncSession = Depends(get_session),
) -> ResourceService:
    db_repo = DatabaseRepository(session)
    return ResourceService(db_repo)


def get_db_repo(
    session: AsyncSession = Depends(get_session),
) -> DatabaseRepository:
    return DatabaseRepository(session)


def get_encrypt_repo() -> EncryptionRepository:
    return EncryptionRepository()


def get_current_user(
    authorization: str = Header(...),
) -> dict:
    if authorization.startswith("Bearer "):
        token = authorization.removeprefix("Bearer ")
        return verify_browser_token(token)
    return verify_telegram_data(authorization)


def get_active_session(user: dict = Depends(get_current_user)):
    user_id = user.get("id")
    if not session_manager.is_active(user_id):
        raise HTTPException(status_code=401, detail="Session expired")
    return {"user_id": user_id}


def get_master_password(session: dict = Depends(get_active_session)) -> str:
    password = session_manager.get_master_password(session["user_id"])
    if not password:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return password
