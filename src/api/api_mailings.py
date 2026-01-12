from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models.mailing import Mailing, MailingStatus
from src.schemas.schema_mailing import MailingCreate, MailingRead
from src.tasks.mailing_tasks import send_mailing_task


router = APIRouter(prefix="/mailings", tags=["Рассылки"])


@router.post("/", response_model=MailingRead, status_code=status.HTTP_201_CREATED)
async def create_and_start_mailing(mailing_data: MailingCreate, db: AsyncSession = Depends(get_db)):
    """Создание новой рассылки"""

    # 1. Сохраняем информацию о рассылке в базу
    new_mailing = Mailing(
        subject=mailing_data.subject,
        content=mailing_data.content,
        status=MailingStatus.PENDING
    )
    db.add(new_mailing)
    
    # 2. Сохраняем
    await db.commit()
    await db.refresh(new_mailing)

    # 3. Копируем данные в простые переменные ПЕРЕД отправкой в Celery
    m_id = new_mailing.id
    m_subject = str(new_mailing.subject)
    m_content = str(new_mailing.content)

    # 4. ЗАПУСКАЕМ ЗАДАЧУ
    send_mailing_task.delay(
        mailing_id=m_id,  # Аргумент должен идти ПЕРВЫМ 
        mailing_subject=m_subject,
        mailing_content=m_content
    )
    # 5. Возвращаем объект Pydantic явно
    return MailingRead.model_validate(new_mailing)

