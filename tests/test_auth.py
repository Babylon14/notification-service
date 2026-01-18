import pytest


@pytest.mark.asyncio
async def test_register_user(client):
    """Тест на регистрацию нового пользователя"""

    response = await client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_login_user(client):
    """Тест на авторизацию пользователя"""

    # Сначала регистрируем пользователя
    await client.post("/auth/register", json={
        "email": "login@example.com",
        "password": "password123"
    })
    # Логинимся (через Form Data, как в Swagger) 
    response = await client.post("/auth/login", data={
        "username": "login@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

    