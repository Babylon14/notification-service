from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings


# 1. Создание асинхронного движка SQLAlchemy
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True, # Выводит SQL-запросы в консоль (для разработки)
    future=True
)

# 2. Фабрика сессий
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# 3. Базовый класс для моделей
class Base(DeclarativeBase):
    pass


# 4. Зависимость для FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()




