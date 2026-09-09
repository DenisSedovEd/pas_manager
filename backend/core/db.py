from typing import AsyncGenerator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from backend.core.config import settings
from backend.models.category import CategoryTable

async_engine: AsyncEngine = create_async_engine(
    settings.db.url,
    echo=settings.db.echo,
    future=settings.db.future,
    pool_pre_ping=True,
)

async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def init_db():
    """Инициализировать БД и создать дефолтные данные."""
    async with async_session() as session:
        result = await session.execute(
            select(CategoryTable).where(
                CategoryTable.category_name == "Other",
                CategoryTable.parent_id.is_(None),
            )
        )
        if not result.scalar():
            other_category = CategoryTable(
                category_name="Other",
                description="📌",
            )
            session.add(other_category)
            await session.commit()
