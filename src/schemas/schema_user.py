from pydantic import BaseModel, ConfigDict, EmailStr


# Базовая схема с общими полями при регистрации
class UserCreate(BaseModel):
    email: EmailStr
    password: str


# Что возвращаем пользователю (без пароля!)
class UserRead(BaseModel):
    id: int
    email: EmailStr
    
    model_config = ConfigDict(from_attributes=True)


# Схема для выдачи токена
class Token(BaseModel):
    access_token: str
    token_type: str

