from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models.mailing import Mailing
from src.schemas.schema_mailing import MailingCreate, MailingRead
from src.tasks.mailing_tasks import send_mailing_task


router = APIRouter(prefix="/mailings", tags=["Рассылки"])


@router.post("/", response_model=MailingRead, status_code=status.HTTP_201_CREATED)
async def create_and_start_mailing(mailing_data: MailingCreate, db: AsyncSession = Depends(get_db)):
    """Создание новой рассылки"""

    # 1. Сохраняем информацию о рассылке в базу
    new_mailing = Mailing(**mailing_data.model_dump())
    db.add(new_mailing)
    await db.commit()
    await db.refresh(new_mailing) # Чтобы получить ID и дату создания из БД

    # 2. ЗАПУСКАЕМ ФОНОВУЮ ЗАДАЧУ
    send_mailing_task.delay(
        mailing_subject=new_mailing.subject,
        mailing_content=new_mailing.content
    )

    return new_mailing

