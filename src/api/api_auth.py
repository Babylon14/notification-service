from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database import get_db
from src.models.user import User
from src.schemas.schema_user import UserCreate, UserRead
from src.core.security import get_password_hash


router = APIRouter(prefix="/auth", tags=["Авторизация"])

@router.post(path="/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)) -> UserRead:
    """Регистрация нового пользователя"""

    # 1. Проверка, существует ли уже пользователь с таким email
    query = select(User).where(User.email == user_data.email)
    result = await db.execute(query)
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email был уже зарегистрирован!"
        )
    # 2. Хешируем пароль
    hashed_pass = get_password_hash(user_data.password)

    # 3. Создаем объект пользователя
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_pass,
        is_active=True
    )
    # 4. Сохраняем в базу данных
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


