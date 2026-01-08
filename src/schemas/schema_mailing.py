from pydantic import BaseModel, ConfigDict
from datetime import datetime


# Базовая схема с общими полями
class MailingCreate(BaseModel):
    subject: str
    content: str


# Схема для ответа (выходные данные)
class MailingRead(MailingCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

