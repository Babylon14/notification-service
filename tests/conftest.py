import os
import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from dotenv import load_dotenv

load_dotenv()

from src.main import app
from src.database import Base, get_db


# Используем тестовую базу данных (можно создать отдельную в Docker)
TEST_DATABASE_URL = (
    f"postgresql+asyncpg://"
    f"{os.getenv('POSTGRES_USER')}:"
    f"{os.getenv('POSTGRES_PASSWORD')}@"
    f"db:{os.getenv('POSTGRES_PORT')}/"
    f"test_db"
)

engine_test = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
async_session_test = sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(autouse=True)
async def prepare_database():
    """Инициализация таблиц перед всеми тестами"""
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# scope="function" по умолчанию
@pytest.fixture
async def db_session():
    """Фикстура сессии"""
    async with async_session_test() as session:
        yield session
        await session.rollback() # Чистим за собой


# scope="function"
@pytest.fixture
async def client(db_session):
    """Фикстура клиента"""

    # Подменяем зависимость внутри этой конкретной фикстуры
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()

    