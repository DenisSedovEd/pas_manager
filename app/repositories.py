import logging
from typing import Optional, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.crypto.encryption import (
    decrypt_data,
    encrypt_data,
)
from app.crypto.exception import InvalidTag
from app.models.account import Account
from app.schemas import CreateAccountSchema, ResponseAccountSchema

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


class AccountRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create_account(
        self, data: CreateAccountSchema, master_password: str
    ) -> Account:
        new_data = f"{data.username}|{data.password}"

        enc_data = encrypt_data(
            new_data,
            master_password,
        )

        new_account = Account(
            service_name=data.service_name,
            user_name=data.username,
            encrypted_data=enc_data["encrypted_data"],
            salt=enc_data["salt"],
            nonce=enc_data["nonce"],
            tag=enc_data["tag"],
        )

        self._session.add(new_account)
        await self._session.commit()

        await self._session.refresh(new_account)
        return new_account

    async def get_account_by_name(
        self, service_name: str, master_password: str
    ) -> Optional[ResponseAccountSchema]:
        stmt = select(Account).where(
            func.lower(Account.service_name) == func.lower(service_name)
        )
        result = await self._session.execute(stmt)
        account = result.scalars().first()

        if not account:
            raise ValueError(f"Сервис {service_name} не найден.")

        try:
            decrypted_payload = decrypt_data(
                account.encrypted_data,
                account.salt,
                account.nonce,
                master_password,
            )
        except InvalidTag as e:
            raise ValueError(f"Неверный мастер пароль: {e}")
        except Exception as e:
            raise ValueError(
                f"Критическая ошибка дешифрования: {type(e).__name__} - {e}"
            )

        if "|" not in decrypted_payload:
            raise ValueError("Ошибка формата данных при дешифровании.")

        user_name, password = decrypted_payload.split("|", 1)

        return ResponseAccountSchema(
            username=user_name,
            password=password,
        )

    async def get_accounts(self) -> Sequence[Account]:
        stmt = select(Account).order_by(Account.service_name)
        result = await self._session.execute(stmt)
        accounts = result.scalars().all()
        logger.info(accounts)
        return accounts


class RepositoryFactory:
    def __init__(self, repo_class):
        self._repo_class = repo_class
        self._context_manager = None
        self._session_object = None

    async def __aenter__(self):
        self._context_manager = get_session()
        self._session_object = await self._context_manager.__aenter__()
        return self._repo_class(self._session_object)

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return await self._context_manager.__aexit__(exc_type, exc_val, exc_tb)


AccountRepository = RepositoryFactory(AccountRepository)
