from sqlalchemy import select, or_

from backend.schemas.account_schema import (
    AccountRequestSchema,
    AccountListItemSchema,
    AccountDetailSchema,
    AccountSuggestionsSchema,
    SearchResultItemSchema,
)
from backend.models.account import Account
from backend.models.category import CategoryTable
from backend.models.resource import ResourceTable
from backend.repositories import DatabaseRepository
from backend.repositories.encryption_repository import EncryptionRepository
from cryptography.exceptions import InvalidTag as CryptoInvalidTag


class AccountService:
    def __init__(
        self,
        db_repo: DatabaseRepository,
        encrypt_repo: EncryptionRepository,
    ):
        self.db_repo = db_repo
        self.encrypt_repo = encrypt_repo

    async def get_accounts_by_category(
        self, category_id: str
    ) -> list[AccountListItemSchema]:
        """Получить все аккаунты платформы (без расшифровки паролей)"""
        accounts = await self.db_repo.get_list(
            Account, filters=Account.category_id == category_id
        )

        result = []
        for account in accounts:
            item = AccountListItemSchema(
                id=account.id,
                label=account.label or "",
                login=account.login,
                category_id=account.category_id,
                resource_id=account.resource_id,
                order=account.order,
            )
            result.append(item)

        return result

    async def get_suggestions(self) -> AccountSuggestionsSchema:
        suggestions = await self.db_repo.get_list(Account)
        emails_set = set()
        phones_set = set()
        labels_set = set()
        logins_set = set()
        for s in suggestions:
            if s.login:
                logins_set.add(s.login)
            if s.email:
                emails_set.add(s.email)
            if s.phone:
                phones_set.add(s.phone)
            if s.label:
                labels_set.add(s.label)

        return AccountSuggestionsSchema(
            login=list(logins_set),
            email=list(emails_set),
            phone=list(phones_set),
            label=list(labels_set),
        )

    async def get_account_decrypted(
        self, account_id: int, master_password: str
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
            raise ValueError(
                "Ключ не подходит. Проверьте мастер-пароль или настройки итераций."
            )

        return AccountDetailSchema(
            id=account.id,
            login=account.login,
            password=decrypted_password,
            email=account.email,
            phone=account.phone,
            label=account.label,
            category_id=account.category_id,
            resource_id=account.resource_id,
        )

    async def create_account(
        self,
        account: AccountRequestSchema,
        master_password: str,
    ) -> AccountDetailSchema:
        """Создать новый аккаунт"""
        enc_data = self.encrypt_repo.encrypt_data(
            account.password,
            master_password,
        )

        new_account = Account(
            login=account.login,
            email=account.email or None,
            phone=account.phone or None,
            label=account.label or "",
            order=account.order,
            category_id=account.category_id,
            resource_id=account.resource_id,
            encrypted_data=enc_data["encrypted_data"],
            salt=enc_data["salt"],
            nonce=enc_data["nonce"],
            tag=enc_data["tag"],
        )

        await self.db_repo.add(new_account)

        detail = AccountDetailSchema(
            id=new_account.id,
            login=new_account.login,
            password=account.password,
            email=new_account.email or None,
            phone=new_account.phone or None,
            label=new_account.label or "",
            category_id=new_account.category_id,
            resource_id=new_account.resource_id,
        )

        return detail

    async def reorder_accounts(self, order_list: list[str]):
        """Пересортируем список аккаунтов"""
        for index, account_id in enumerate(order_list):
            await self.db_repo.update(
                Account,
                filters={"id": str(account_id)},
                values={"order": int(index)},
            )

    async def update_account(
        self,
        account_id: int,
        account: AccountRequestSchema,
        master_password: str,
    ) -> AccountDetailSchema:
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
                "category_id": account.category_id,
                "resource_id": account.resource_id,
                "login": account.login,
                "email": account.email or None,
                "phone": account.phone or None,
                "label": account.label or "",
                "encrypted_data": enc_data["encrypted_data"],
                "salt": enc_data["salt"],
                "nonce": enc_data["nonce"],
                "tag": enc_data["tag"],
            },
        )

        detail = AccountDetailSchema(
            id=account_id,
            login=account.login,
            password=account.password,
            email=account.email or None,
            phone=account.phone or None,
            label=account.label or "",
            category_id=account.category_id,
            resource_id=account.resource_id,
        )

        return detail

    async def delete_account(self, account_id: int) -> None:
        """Удалить аккаунт"""
        account = await self.db_repo.get(Account, filters={"id": account_id})

        if not account:
            raise ValueError(f"Account with id {account_id} not found")

        await self.db_repo.delete(account)

    async def search(self, query: str) -> list[SearchResultItemSchema]:
        """Глобальный поиск по всем полям аккаунтов"""
        q = f"%{query.lower()}%"

        stmt = (
            select(Account, CategoryTable, ResourceTable)
            .join(CategoryTable, Account.category_id == CategoryTable.id)
            .outerjoin(ResourceTable, Account.resource_id == ResourceTable.id)
            .where(
                or_(
                    Account.login.ilike(q),
                    Account.email.ilike(q),
                    Account.phone.ilike(q),
                    Account.label.ilike(q),
                    CategoryTable.category_name.ilike(q),
                    ResourceTable.resource_name.ilike(q),
                )
            )
            .limit(50)
        )

        result = await self.db_repo.session.execute(stmt)
        rows = result.all()

        parent_ids = {cat.parent_id for _, cat, _ in rows if cat.parent_id}
        parent_map: dict[str, CategoryTable] = {}
        if parent_ids:
            parent_stmt = select(CategoryTable).where(CategoryTable.id.in_(parent_ids))
            parent_result = await self.db_repo.session.execute(parent_stmt)
            for parent in parent_result.scalars().all():
                parent_map[parent.id] = parent

        items = []
        for account, category, resource in rows:
            parent_name = None
            if category.parent_id and category.parent_id in parent_map:
                parent_name = parent_map[category.parent_id].category_name

            items.append(
                SearchResultItemSchema(
                    account_id=account.id,
                    login=account.login,
                    label=account.label,
                    email=account.email,
                    phone=account.phone,
                    category_id=category.id,
                    category_name=category.category_name,
                    category_icon=category.icon,
                    parent_category_name=parent_name,
                    resource_id=resource.id if resource else None,
                    resource_name=resource.resource_name if resource else None,
                )
            )

        return items
