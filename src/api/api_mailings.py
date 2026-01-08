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

    # 2. Сохраняем
    await db.commit()
    await db.refresh(new_mailing)

    # 3. Копируем данные в простые переменные ПЕРЕД отправкой в Celery
    m_id = new_mailing.id
    m_subject = str(new_mailing.subject)
    m_content = str(new_mailing.content)
    m_created_at = new_mailing.created_at

    # 4. ЗАПУСКАЕМ ЗАДАЧУ
    send_mailing_task.delay(
        mailing_subject=m_subject,
        mailing_content=m_content
    )

    # 5. Возвращаем чистый объект Pydantic (это уберет ошибку 500)
    return MailingRead(
        id=m_id,
        subject=m_subject,
        content=m_content,
        created_at=m_created_at
    )

