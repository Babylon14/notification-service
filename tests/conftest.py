import asyncio
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.database import Base, get_db


# Используем тестовую базу данных (можно создать отдельную в Docker)
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db"

engine_test = create_async_engine(TEST_DATABASE_URL, echo=False)
async_session_test = sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    """Создаем таблицы перед тестами и удаляем после."""
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session():
    """Фикстура для сессии БД"""
    async with async_session_test() as session:
        yield session


@pytest.fixture
async def client(db_session):
    """Фикстура для асинхронного клиента FastAPI"""
    async def override_get_db():
        yield db_session()

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


    