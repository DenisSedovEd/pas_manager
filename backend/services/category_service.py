import uuid

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.models.category import CategoryTable
from backend.repositories import DatabaseRepository
from backend.schemas.category import CategoryResponseSchema, CategoryRequestSchema

_CATEGORY_OPTIONS = [
    selectinload(CategoryTable.children),
    selectinload(CategoryTable.accounts),
]


class CategoryService:
    def __init__(self, db_repo: DatabaseRepository):
        self.db_repo = db_repo

    def _to_schema(self, category: CategoryTable) -> CategoryResponseSchema:
        return CategoryResponseSchema(
            id=category.id,
            name=category.category_name,
            icon=category.icon,
            description=category.description,
            order=category.order,
            parent_id=category.parent_id,
            accounts_count=len(category.accounts),
            children_count=len(category.children),
        )

    async def get_categories(self) -> list[CategoryResponseSchema]:
        """Вернуть только корневые категории (parent_id IS NULL)"""
        from backend.models.category import CategoryTable as CT
        categories = await self.db_repo.get_list(
            CategoryTable,
            filters=CT.parent_id.is_(None),
            options=_CATEGORY_OPTIONS,
        )
        return [self._to_schema(c) for c in categories]

    async def get_children(self, parent_id: str) -> list[CategoryResponseSchema]:
        """Вернуть подкатегории"""
        from backend.models.category import CategoryTable as CT
        children = await self.db_repo.get_list(
            CategoryTable,
            filters=CT.parent_id == parent_id,
            options=_CATEGORY_OPTIONS,
        )
        return [self._to_schema(c) for c in children]

    async def get_category(self, category_id: str) -> CategoryResponseSchema:
        """Получить одну категорию"""
        category = await self.db_repo.get(
            CategoryTable,
            filters={"id": category_id},
            options=_CATEGORY_OPTIONS,
        )
        if not category:
            raise ValueError(f"Category with id {category_id} not found")
        return self._to_schema(category)

    async def add_category(
        self, category_data: CategoryRequestSchema
    ) -> CategoryResponseSchema:
        """Добавить новую категорию"""
        new_id = str(uuid.uuid4())

        from backend.models.category import CategoryTable as CT
        siblings = await self.db_repo.get_list(
            CategoryTable,
            filters=CT.parent_id == category_data.parent_id if category_data.parent_id else CT.parent_id.is_(None),
        )
        new_order = len(siblings)

        new_category = CategoryTable(
            id=new_id,
            category_name=category_data.name,
            icon=category_data.icon,
            description=category_data.description,
            order=new_order,
            parent_id=category_data.parent_id or None,
        )
        await self.db_repo.add(new_category)

        return CategoryResponseSchema(
            id=new_category.id,
            name=new_category.category_name,
            icon=new_category.icon,
            description=new_category.description,
            accounts_count=0,
            children_count=0,
            order=new_category.order,
            parent_id=new_category.parent_id,
        )

    async def update_category(
        self, category_id: str, category_data: CategoryRequestSchema
    ) -> CategoryResponseSchema:
        """Обновить категорию"""
        category = await self.db_repo.get(
            CategoryTable,
            filters={"id": category_id},
            options=_CATEGORY_OPTIONS,
        )
        if not category:
            raise ValueError(f"Category with id {category_id} not found")

        await self.db_repo.update(
            CategoryTable,
            filters={"id": category_id},
            values={
                "category_name": category_data.name,
                "icon": category_data.icon,
                "description": category_data.description,
                "parent_id": category_data.parent_id or None,
            },
        )

        accounts_count = len(category.accounts)
        children_count = len(category.children)
        return CategoryResponseSchema(
            id=category_id,
            name=category_data.name,
            icon=category_data.icon,
            description=category_data.description,
            accounts_count=accounts_count,
            children_count=children_count,
            order=category.order,
            parent_id=category_data.parent_id or None,
        )

    async def reorder_categories(self, order_list: list[str]):
        """Пересортировать список категорий"""
        for index, category_id in enumerate(order_list):
            await self.db_repo.update(
                CategoryTable,
                filters={"id": str(category_id)},
                values={"order": int(index)},
            )

    async def delete_category(self, category_id: str, transfer_accounts: bool = True):
        """Удалить категорию"""
        category = await self.db_repo.get(CategoryTable, filters={"id": category_id})
        if not category:
            raise ValueError(f"Category with id {category_id} not found")

        if category.category_name == "Other" and category.parent_id is None:
            raise ValueError("Нельзя удалить системную категорию 'Other'")

        if transfer_accounts:
            from backend.models.category import CategoryTable as CT
            other_category = await self.db_repo.get(
                CategoryTable, filters={"category_name": "Other"}
            )
            if not other_category:
                other_category = CategoryTable(category_name="Other", description="📌")
                await self.db_repo.add(other_category)

            from backend.models.account import Account
            await self.db_repo.update(
                Account,
                filters={"category_id": category_id},
                values={"category_id": str(other_category.id)},
            )

        await self.db_repo.delete(category)
