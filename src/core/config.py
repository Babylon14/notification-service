"""Настройки БД"""
from pydantic_settings import BaseSettings, SettingsConfigDict


# Описание настроек через Pydantic
class Settings(BaseSettings):
    # Эти переменные автоматически взяты из .env

    # Данные для БД и Redis
    DATABASE_URL: str
    REDIS_URL: str
    
    # Данные для PgAdmin (Pydantic будет искать их в .env)
    PGADMIN_EMAIL: str
    PGADMIN_PASSWORD: str
    
    # Настройки почты
    SMTP_HOST: str = "sandbox.smtp.mailtrap.io"
    SMTP_PORT: int = 2525
    SMTP_USER: str
    SMTP_PASSWORD: str
    
    # Безопасность
    SECRET_KEY: str
    ALGORITHM: str

    # Настройки БД
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str

    # Настройка для чтения .env файла
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        env_file_encoding="utf-8"
    )


settings = Settings()


