from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database import get_db
from src.models.contact import Contact
from src.schemas.schema_contact import ContactCreate, ContactRead


router = APIRouter(prefix="/contacts", tags=["Контакты"])

@router.post("/", response_model=ContactRead, status_code=status.HTTP_201_CREATED)
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

