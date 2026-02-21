from models import Account
from repositories import DatabaseRepository
from repositories.encryption_repository import EncryptionRepository
from schemas import AccountSchema, InvalidTag


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
        account: AccountSchema,
        master_password: str,
    ) -> Account:
        new_account_creds = f"{account.username}|{account.password}"

        enc_data = self.encrypt_repo.encrypt_data(
            new_account_creds,
            master_password,
        )

        new_account = Account(
            service_name=account.service_name,
            user_name=account.username,
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
    ) -> AccountSchema:
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

        return AccountSchema(
            service_name=search_account.service_name,
            username=user_name,
            password=password,
        )

    async def get_accounts(self) -> list[AccountSchema]:
        accounts_list = await self.db_repo.get_list(Account)
        res = []
        for account in accounts_list:
            res.append(
                AccountSchema(
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
    ) -> AccountSchema:
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

        return AccountSchema(
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
