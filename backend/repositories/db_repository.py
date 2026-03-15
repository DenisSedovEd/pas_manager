from sqlalchemy import desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import Platform


class DatabaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, model_instance):
        """Добавить объект в БД"""
        self.session.add(model_instance)
        await self.session.commit()
        await self.session.refresh(model_instance)
        return model_instance

    async def update(self, model, filters: dict, values: dict):
        """Обновить объект в БД"""
        query = update(model).filter_by(**filters).values(**values)
        await self.session.execute(query)
        await self.session.commit()

    async def get(self, model, filters: dict):
        """Получить один объект по фильтрам"""
        query = select(model).filter_by(**filters)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_list(self, model, limit: int = 100, filters=None, options=None):
        """Получить список объектов с поддержкой подгрузки связей"""
        query = select(model).limit(limit)

        if filters is not None:
            query = query.where(filters)

        if hasattr(model, 'order'):
            query = query.order_by(model.order.asc())



        if options is not None:
            # Это позволит нам добавить selectinload в сервисе
            query = query.options(*options)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def delete(self, model_instance):
        """Удалить объект из БД"""
        await self.session.delete(model_instance)
        await self.session.commit()
        return model_instance