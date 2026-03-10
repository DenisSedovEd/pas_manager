from contextlib import asynccontextmanager

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import async_session, get_session
from src.repositories import encryption_repository, DatabaseRepository
from src.repositories.encryption_repository import EncryptionRepository
from src.services.account_service import AccountService
from src.services.platform_service import PlatformService


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
