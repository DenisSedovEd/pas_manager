from functools import wraps
from typing import Optional, List, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import CreateAccountSchema
from app.core.db import get_session
from app.models.account import Account

from app.crypto import encryption
from schemas import ResponseAccountSchema


def with_session(handler):
    @wraps(handler)
    async def wrapper(update, context, *args, **kwargs):
        async with get_session() as session:
            repo = AccountRepository(session)
            return await handler(update, context, repo, *args, **kwargs)

    return wrapper


class AccountRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, data: CreateAccountSchema, master_password: str) -> Account:
        full_data = f"{data.username}|{data.password}"

        enc_data = encryption.encrypt_data(
            full_data,
            encryption.derive_key(master_password, encryption.generate_salt()),
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

    async def get_decrypted(
        self, service_name: str, master_password: str
    ) -> Optional[ResponseAccountSchema]:
        stmt = select(Account).filter_by(service_name=service_name)
        result = await self._session.execute(stmt)
        account = result.scalar_one_or_none()

        if not account:
            return None

        try:
            decrypted_full_data = encryption.decode_and_decrypt(
                account.encrypted_data,
                account.salt,
                account.nonce,
                account.tag,
                master_password,
            )
        except ValueError as e:
            raise ValueError(e)
        except Exception:
            raise ValueError("Ошибка дешифрования или повреждение данных")

    async def get_accounts(self) -> Sequence[Account]:
        stmt = select(Account)
        result = await self._session.execute(stmt)
        accounts = result.scalars().all()
        return accounts
