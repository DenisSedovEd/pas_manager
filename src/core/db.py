from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool
from src.models.platform import Platform

from sqlalchemy import select
from src.core.config import settings

async_engine: AsyncEngine = create_async_engine(
    settings.db.url,
    echo=settings.db.echo,
    future=settings.db.future,
    poolclass=StaticPool,
    connect_args={
        "timeout": 30,
        "check_same_thread": False,
    },
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
    """Инициализировать БД и создать дефолтные данные"""
    # async with async_engine.begin() as conn:
    #     from src.models.base import Base
    #     await conn.run_sync(Base.metadata.create_all)

    # Создаём дефолтную платформу
    async with async_session() as session:

        result = await session.execute(
            select(Platform).where(Platform.platform_name == "Other")
        )
        if not result.scalar():
            other_platform = Platform(
                platform_name="Other",
                description="📌"
            )
            session.add(other_platform)
            await session.commit()