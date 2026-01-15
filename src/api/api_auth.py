from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database import get_db
from src.models.user import User
from src.schemas.schema_user import UserCreate, UserRead, Token
from src.core.security import get_password_hash, verify_password, create_access_token


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
        hash_password=hashed_pass,
        is_active=True
    )
    # 4. Сохраняем в базу данных
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.post(path="/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
    ) -> Token:
    """Аутентификация пользователя"""

    # 1. Проверяем, существует ли пользователь с таким email
    query = select(User).where(User.email == form_data.username)
    result = await db.execute(query)
    user = result.scalars().first()

    # 2. Проверяем: есть ли такой юзер и совпадает ли хеш пароля
    if not user or not verify_password(form_data.password, user.hash_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # 3. Создаем JWT токен
    access_token = create_access_token(subject=user.email)

    return {"access_token": access_token, "token_type": "bearer"}

