from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional


# Базовая схема с общими полями
class ContactBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = True


# Схема для создания (входные данные)
class ContactCreate(ContactBase):
    pass


# Схема для обновления (входные данные)
class ContactUpdate(ContactBase):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None


# Схема для ответа (выходные данные)
class ContactRead(ContactBase):
    id: int
    is_active: bool
    created_at: datetime

    # Важнейшая настройка для SQLAlchemy!
    model_config = ConfigDict(from_attributes=True) # Pydantic читает данные прямо из объектов SQLAlchemy


