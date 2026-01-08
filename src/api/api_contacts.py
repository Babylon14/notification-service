from typing import List
from pydantic import EmailStr
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database import get_db
from src.models.contact import Contact
from src.schemas.schema_contact import ContactCreate, ContactRead


router = APIRouter(prefix="/contacts", tags=["Контакты"])

@router.post(path="/", response_model=ContactRead, status_code=status.HTTP_201_CREATED)
async def create_contact(contact_data: ContactCreate, db: AsyncSession = Depends(get_db)) -> ContactRead:
    """Создание контакта"""

    # 1. Проверяем, существует ли уже контакт с таким email
    query = select(Contact).where(Contact.email == contact_data.email)
    result = await db.execute(query) # Результат запроса
    existing_contact = result.scalar_one_or_none()

    if existing_contact: #
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Контакт с таким email уже существует"
        )
    # 2. Создаем объект модели из данных схемы
    new_contact = Contact(**contact_data.model_dump())

    # 3. Добавляем контакт в базу данных
    db.add(new_contact)
    await db.commit()
    await db.refresh(new_contact) # Чтобы получить ID и дату создания из БДвляем контакт

    # 4. Возвращаем созданный контакт
    return new_contact


@router.get(path="/", response_model=List[ContactRead])
async def get_contacts(
    limit: int = 10, # количество записей (по умолчанию 10)
    offset: int = 0, # сколько записей пропустить (по умолчанию 0)
    db: AsyncSession = Depends(get_db)
    ) -> List[ContactRead]:
    """Получение всех контактов"""

    # Создаем запрос: выборка всех контактов и сортировка по ID
    query = select(Contact).offset(offset).limit(limit).order_by(Contact.id)
    result = await db.execute(query)
    result = result.scalars().all()

    return result 


@router.get(path="/search", response_model=ContactRead, status_code=status.HTTP_200_OK)
async def search_contact_by_email(email=EmailStr, db: AsyncSession = Depends(get_db)) -> ContactRead:
    """Поиск конкретного контакта по его email."""

    query = select(Contact).where(Contact.email == email) # Запрос
    result = await db.execute(query)                      # Выполняем запрос
    contact = result.scalar_one_or_none()                 # Достаем данный объект или None

    # Если не нашли — кидаем 404
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Контакт с email {email} не найден"
        )

    return contact


@router.delete(path="/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int, db: AsyncSession = Depends(get_db)) -> Response:
    """Удаление контакта по его ID"""

    # 1. Ищем контакт
    query = select(Contact).where(Contact.id == contact_id)
    result = await db.execute(query)
    contact = result.scalar_one_or_none()

    # 2. Если контакт не нашли, кидаем 404
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Контакт с id {contact_id} не найден"
        )

    # 3. Удаляем контакт
    await db.delete(contact)
    await db.commit()

    # 4. Возвращаем пустой ответ (так принято для 204 статуса)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

