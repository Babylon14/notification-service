"""Подключение к БД (Async Engine)"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator

from database import AsyncSessionLocal


# Описание настроек через Pydantic
class Settings(BaseSettings):
    # Эти переменные автоматически взяты из .env
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str

    # Настройка для чтения .env файла
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()


# Зависимости для FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

