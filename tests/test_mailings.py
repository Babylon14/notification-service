import pytest


@pytest.fixture
async def auth_token(client):
    """Фикстура, которая регистрирует пользователя и возвращает токен."""

    email = "victor@example.com"
    password = "testpassworddd"

    # Регистрируем пользователя
    await client.post("/auth/register", json={"email": email, "password": password})
    # Авторизуемся
    response = await client.post("/auth/login", data={"username": email, "password": password})
    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_create_mailing_authenticated(client, auth_token):
    """Тест на создание авторизованной рассылки"""

    response = await client.post("/mailings/",
        json={"subject": "Тестовая рассылка", "content": "Тестовое содержание"},
        headers={"Authorization": f"Bearer {auth_token}"
    })
    assert response.status_code == 201
    assert response.json()["subject"] == "Тестовая рассылка"


@pytest.mark.asyncio
async def test_create_mailing_unauthorized(client):
    """Тест на создание НЕ авторизованной рассылки"""
    
    response = await client.post("/mailings/",
        json={"subject": "Тестовая рассылка", "content": "Тестовое содержание"}
    )
    assert response.status_code == 401  # 401 - Не авторизован







