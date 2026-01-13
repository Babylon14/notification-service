from pydantic import BaseModel, EmailStr


# Базовая схема с общими полями при регистрации
class UserBase(BaseModel):
    email: EmailStr
    password: str


# Что возвращаем пользователю (без пароля!)
class UserRead(BaseModel):
    id: int
    email: EmailStr
    
    class Config:
        from_attributes = True


# Схема для выдачи токена
class Tocken(BaseModel):
    access_token: str
    token_type: str

    