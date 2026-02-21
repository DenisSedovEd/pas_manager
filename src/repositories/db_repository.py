from sqlalchemy import desc, select, update
from sqlalchemy.ext.asyncio import AsyncSession


class DatabaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, model_instance):
        self.session.add(model_instance)
        await self.session.commit()
        await self.session.refresh(model_instance)
        return model_instance

    async def update(self, model, filters: dict, values):
        query = update(model).filter_by(**filters).values(**values)
        await self.session.execute(query)
        await self.session.commit()

    async def get(self, model, filters: dict):
        query = select(model).filter_by(**filters)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_list(self, model, limit: int = 20):
        query = select(model).order_by(desc(model.service_name)).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def delete(self, model):
        await self.session.delete(model)
        await self.session.commit()
        return model
