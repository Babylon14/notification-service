from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from src.core.config import settings


# Создание асинхронного движка SQLAlchemy
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True, # Выводит SQL-запросы в консоль (для разработки)
    future=True
)

# Фабрика сессий
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Базовый класс для моделей
class Base(DeclarativeBase):
    pass


