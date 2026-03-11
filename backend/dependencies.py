from contextlib import asynccontextmanager

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db import async_session, get_session
from backend.repositories import encryption_repository, DatabaseRepository
from backend.repositories.encryption_repository import EncryptionRepository
from backend.services.account_service import AccountService
from backend.services.platform_service import PlatformService


def get_account_service(
        session: AsyncSession = Depends(get_session),
) -> AccountService:
    db_repo = DatabaseRepository(session)
    encrypt_repo = EncryptionRepository()
    return AccountService(db_repo, encrypt_repo)


def get_platform_service(
        session: AsyncSession = Depends(get_session),
) -> PlatformService:
    db_repo = DatabaseRepository(session)
    return PlatformService(db_repo)


def get_db_repo(
        session: AsyncSession = Depends(get_session),
) -> DatabaseRepository:
    return DatabaseRepository(session)

def get_encrypt_repo() -> EncryptionRepository:
    return EncryptionRepository()

# @asynccontextmanager
# async def get_account_service():
#     async for session in get_session():
#         db_repo = DatabaseRepository(session)
#         encrypt_repo = EncryptionRepository()
#         account_service = AccountService(
#             db_repo,
#             encrypt_repo,
#         )
#         try:
#             yield account_service
#         except Exception:
#             await session.rollback()
#             raise
#         finally:
#             await session.close()
