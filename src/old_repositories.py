import logging
from typing import Optional, Sequence

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_session
from src.repositories.encryption_repository import (
    decrypt_data,
    encrypt_data,
)
from src.crypto.exception import InvalidTag
from src.models.account import Account
from src.schemas import CreateAccountSchema, ResponseAccountSchema, EditAccountSchema

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

    async def edit_account(
        self, edited_service: EditAccountSchema, master_password: str
    ):
        new_data = {}
        old_data = await self.get_account_by_name(
            service_name=edited_service.service_name,
            master_password=master_password,
        )
        new_data["service_name"] = old_data.service_name
        if edited_service.username:
            new_data["username"] = edited_service.username
        if edited_service.password:
            new_data["password"] = edited_service.password

        new_data_for_crypto = f"{new_data["username"]}|{new_data["password"]}"

        enc_data = encrypt_data(
            new_data_for_crypto,
            master_password,
        )

        new_account = Account(
            service_name=old_data.service_name,
            user_name=old_data.username,
            encrypted_data=enc_data["encrypted_data"],
            salt=enc_data["salt"],
            nonce=enc_data["nonce"],
            tag=enc_data["tag"],
        )
        stmt = update(Account).where(
            Account.service_name == new_account.service_name,
        )
        await self._session.execute(stmt)
        await self._session.commit()
        await self._session.refresh(new_account)
        return new_account


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
