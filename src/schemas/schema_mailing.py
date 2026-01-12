from pydantic import BaseModel, ConfigDict
from datetime import datetime

from src.models.mailing import MailingStatus


# Базовая схема с общими полями
class MailingCreate(BaseModel):
    subject: str
    content: str


# Схема для ответа (выходные данные)
class MailingRead(MailingCreate):
    id: int
    status: MailingStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

