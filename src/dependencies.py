from contextlib import asynccontextmanager


from src.core.db import async_session, get_session
from src.repositories import encryption_repository, DatabaseRepository
from src.repositories.encryption_repository import EncryptionRepository
from src.services.account_service import AccountService


@asynccontextmanager
async def get_account_service():
    async for session in get_session():
        db_repo = DatabaseRepository(session)
        encrypt_repo = EncryptionRepository()
        account_service = AccountService(
            db_repo,
            encrypt_repo,
        )
        try:
            yield account_service
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
