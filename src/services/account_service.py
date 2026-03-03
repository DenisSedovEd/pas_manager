import uuid

from src.schemas.account import AccountRequestSchema, AccountResponseSchema
from src.models.account import Account
from src.repositories import DatabaseRepository
from src.repositories.encryption_repository import EncryptionRepository


class AccountService:
    def __init__(
        self,
        db_repo: DatabaseRepository,
        encrypt_repo: EncryptionRepository,
    ):
        self.db_repo = db_repo
        self.encrypt_repo = encrypt_repo

    async def create_account(
        self,
        account: AccountRequestSchema,
        master_password: str,
        platform_id: uuid.UUID,
    ) -> Account:
        new_account_creds = f"{account.user_name}|{account.password}"

        enc_data = self.encrypt_repo.encrypt_data(
            new_account_creds,
            master_password,
        )

        new_account = Account(
            user_name=account.user_name,
            platform_id=platform_id,
            encrypted_data=enc_data["encrypted_data"],
            salt=enc_data["salt"],
            nonce=enc_data["nonce"],
            tag=enc_data["tag"],
        )
        await self.db_repo.add(new_account)

        return new_account

    async def get_account(
        self,
        service_name: str,
        master_password: str,
    ) -> AccountResponseSchema:
        search_account = await self.db_repo.get(
            Account,
            filters={"service_name": service_name},
        )
        if not search_account:
            raise ValueError(f"Сервис {service_name} не найден.")

        try:
            decrypted_payload = self.encrypt_repo.decrypt_data(
                search_account.encrypted_data,
                search_account.salt,
                search_account.nonce,
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

        return AccountResponseSchema(
            service_name=search_account.service_name,
            username=user_name,
            password=password,
        )

    async def get_accounts(self) -> list[AccountResponseSchema]:
        accounts_list = await self.db_repo.get_list(Account)
        res = []
        for account in accounts_list:
            res.append(
                AccountResponseSchema(
                    service_name=account.service_name,
                    username=account.user_name,
                    password="",
                )
            )
        return res

    async def edit_account(
        self,
        service_name: str,
        master_password: str,
        new_username: str | None = None,
        new_password: str | None = None,
    ) -> AccountResponseSchema:
        current_account = await self.get_account(service_name, master_password)

        final_username = (
            new_username
            if new_username and new_username != "-"
            else current_account.username
        )
        final_password = (
            new_password
            if new_password and new_password != "-"
            else current_account.password
        )

        new_creds = f"{final_username}|{final_password}"
        enc_data = self.encrypt_repo.encrypt_data(new_creds, master_password)

        search_account = await self.db_repo.get(
            Account, filters={"service_name": service_name}
        )
        await self.db_repo.update(
            Account,
            filters={"id": search_account.id},
            values={
                "user_name": final_username,
                "encrypted_data": enc_data["encrypted_data"],
                "salt": enc_data["salt"],
                "nonce": enc_data["nonce"],
                "tag": enc_data["tag"],
            },
        )

        return AccountResponseSchema(
            service_name=service_name,
            username=final_username,
            password=final_password,
        )

    async def delete_account(
        self,
        service_name: str,
        master_password: str,
    ) -> bool:
        await self.get_account(service_name, master_password)

        search_account = await self.db_repo.get(
            Account, filters={"service_name": service_name}
        )
        if not search_account:
            raise ValueError
        await self.db_repo.delete(search_account)
        return True
