from backend.models.category import CategoryTable
from backend.repositories import DatabaseRepository
from backend.schemas.category import CategoryResponseSchema, CategoryRequestSchema
import uuid


class CategoryService:
    def __init__(self, db_repo: DatabaseRepository):
        self.db_repo = db_repo

    async def get_categories(self) -> list[CategoryResponseSchema]:
        categories = await self.db_repo.get_list(CategoryTable)

        result = []
        for category in categories:
            accounts_count = len(category.accounts) if category.accounts else 0
            response = CategoryResponseSchema(
                id=category.id,
                name=category.category_name,
                icon=category.icon,
                description=category.description,
                order=category.order,
                accounts_count=accounts_count,
            )
            result.append(response)

        return result

    async def get_category(self, category_id: str) -> CategoryResponseSchema:
        """Получить одну платформу"""
        category = await self.db_repo.get(CategoryTable, filters={"id": category_id})

        if not category:
            raise ValueError(f"Category with id {category_id} not found")

        accounts_count = len(category.accounts) if category.accounts else 0
        return CategoryResponseSchema(
            id=category.id,
            name=category.category_name,
            icon=category.icon,
            description=category.description,
            order=category.order,
            accounts_count=accounts_count,
        )

    async def add_category(self, category_data: CategoryRequestSchema) -> CategoryResponseSchema:
        """Добавить новую платформу"""
        new_id = str(uuid.uuid4())

        existing_categories = await self.db_repo.get_list(CategoryTable)
        new_order = len(existing_categories)

        new_category = CategoryTable(
            id=new_id,
            category_name=category_data.name,
            icon=category_data.icon,
            description=category_data.description,
            order=new_order,
        )
        await self.db_repo.add(new_category)

        return CategoryResponseSchema(
            id=new_category.id,
            name=new_category.category_name,
            icon=new_category.icon,
            description=new_category.description,
            accounts_count=0,
            order=new_category.order,
        )

    async def update_category(self, category_id: str, category_data: CategoryRequestSchema) -> CategoryResponseSchema:
        """Обновить платформу"""
        category = await self.db_repo.get(CategoryTable, filters={"id": category_id})

        if not category:
            raise ValueError(f"Category with id {category_id} not found")

        await self.db_repo.update(
            CategoryTable,
            filters={"id": category_id},
            values={
                "category_name": category_data.name,
                'icon': category_data.icon,
                "description": category_data.description,
            }
        )

        accounts_count = len(category.accounts) if category.accounts else 0
        return CategoryResponseSchema(
            id=category_id,
            name=category_data.name,
            icon=category_data.icon,
            description=category_data.description,
            accounts_count=accounts_count,
            order=category.order,
        )

    async def reorder_categories(self, order_list: list[str]):
        """Пересортируем список платформ"""
        for index, category_id in enumerate(order_list):
            await self.db_repo.update(
                CategoryTable,
                filters={"id": str(category_id)},
                values={"order": int(index) },
            )



    async def delete_category(self, category_id: str, transfer_accounts: bool = True):
        """Удалить платформу с выбором: перенос или удаление аккаунтов"""
        category = await self.db_repo.get(CategoryTable, filters={"id": category_id})
        if not category:
            raise ValueError(f"Categorywith id {category_id} not found")

        if category.category_name == "Other":
            raise ValueError("Нельзя удалить системную категорию 'Other'")

        if transfer_accounts:
            other_category = await self.db_repo.get(CategoryTable, filters={"category_name": "Other"})
            if not other_category:
                other_category = CategoryTable(
                    category_name="Other",
                    description="🌐"
                )
                await self.db_repo.add(other_category)

            from backend.models.account import Account
            await self.db_repo.update(
                Account,
                filters={"category_id": category_id},
                values={"category_id": str(other_category.id)}
            )

        await self.db_repo.delete(category)