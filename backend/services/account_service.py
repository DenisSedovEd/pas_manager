import uuid
from backend.schemas.account import AccountRequestSchema, AccountListItemSchema, AccountDetailSchema, AccountResponseSchema
from backend.models.account import Account
from backend.repositories import DatabaseRepository
from backend.repositories.encryption_repository import EncryptionRepository
from cryptography.exceptions import InvalidTag as CryptoInvalidTag
# from src.schemas.crypto import InvalidTag


class AccountService:
    def __init__(
            self,
            db_repo: DatabaseRepository,
            encrypt_repo: EncryptionRepository,
    ):
        self.db_repo = db_repo
        self.encrypt_repo = encrypt_repo

    async def get_accounts_by_platform(self, platform_id: str) -> list[AccountListItemSchema]:
        """Получить все аккаунты платформы (без расшифровки паролей)"""
        accounts = await self.db_repo.get_list(
            Account, filters=Account.platform_id == platform_id
        )

        result = []
        for account in accounts:
            item = AccountListItemSchema(
                id=account.id,
                label=account.tags or account.user_name,
                login=account.user_name,
                platform_id=account.platform_id,
                order=account.order,
            )
            result.append(item)

        return result

    async def get_account_decrypted(
            self,
            account_id: int,
            master_password: str
    ) -> AccountDetailSchema:
        """Получить расшифрованные данные аккаунта"""
        account = await self.db_repo.get(Account, filters={"id": account_id})

        if not account:
            raise ValueError(f"Account with id {account_id} not found")

        try:
            decrypted_password = self.encrypt_repo.decrypt_data(
                account.encrypted_data,
                account.salt,
                account.nonce,
                master_password,
            )
        except CryptoInvalidTag:
            raise ValueError("Ключ не подходит. Проверьте мастер-пароль или настройки итераций.")

        return AccountDetailSchema(
            id=account.id,
            login=account.user_name,
            password=decrypted_password,
            email=account.email,
            phone=account.phone,
            label=account.tags,
            platform_id=account.platform_id,
        )

    async def create_account(
            self,
            account: AccountRequestSchema,
            master_password: str,
    ) -> AccountResponseSchema:
        """Создать новый аккаунт"""
        # Шифруем пароль
        enc_data = self.encrypt_repo.encrypt_data(
            account.password,
            master_password,
        )

        new_account = Account(
            user_name=account.login,
            email=account.email or None,
            phone=account.phone or None,
            tags=account.label or account.login,
            order=account.order,
            platform_id=account.platform_id,  # ← Строка
            encrypted_data=enc_data["encrypted_data"],
            salt=enc_data["salt"],
            nonce=enc_data["nonce"],
            tag=enc_data["tag"],
        )

        await self.db_repo.add(new_account)

        detail = AccountDetailSchema(
            id=new_account.id,
            login=new_account.user_name,
            password=account.password,
            email=new_account.email or "",
            phone=new_account.phone or "",
            label=new_account.tags or new_account.user_name,
            platform_id=new_account.platform_id,
        )

        return AccountResponseSchema(
            status="success",
            message="Account created successfully",
            data=detail
        )

    async def reorder_accounts(self, order_list: list[str]):
        """Пересортируем список аккаунтов"""
        for index, account_id in enumerate(order_list):
            await self.db_repo.update(
                Account,
                filters={"id": str(account_id)},
                values={"order": int(index) },
            )
        return {'status': 'ok'}

    async def update_account(
            self,
            account_id: int,
            account: AccountRequestSchema,
            master_password: str,
    ) -> AccountResponseSchema:
        """Обновить аккаунт"""
        existing = await self.db_repo.get(Account, filters={"id": account_id})

        if not existing:
            raise ValueError(f"Account with id {account_id} not found")

        # Шифруем новый пароль
        enc_data = self.encrypt_repo.encrypt_data(
            account.password,
            master_password,
        )

        await self.db_repo.update(
            Account,
            filters={"id": account_id},
            values={
                "platform_id": account.platform_id,
                "user_name": account.login,
                "email": account.email or None,
                "phone": account.phone or None,
                "tags": account.label or account.login,
                "encrypted_data": enc_data["encrypted_data"],
                "salt": enc_data["salt"],
                "nonce": enc_data["nonce"],
                "tag": enc_data["tag"],
            }
        )

        detail = AccountDetailSchema(
            id=account_id,
            login=account.login,
            password=account.password,
            email=account.email or "",
            phone=account.phone or "",
            label=account.label or account.login,
            platform_id=account.platform_id,
        )

        return AccountResponseSchema(
            status="success",
            message="Account updated successfully",
            data=detail
        )

    async def delete_account(self, account_id: int) -> AccountResponseSchema:
        """Удалить аккаунт"""
        account = await self.db_repo.get(Account, filters={"id": account_id})

        if not account:
            raise ValueError(f"Account with id {account_id} not found")

        await self.db_repo.delete(account)

        return AccountResponseSchema(
            status="success",
            message="Account deleted successfully",
            data=None
        )