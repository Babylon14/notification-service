import asyncio
import logging 

from src.tasks.celery_app import celery_app
from src.database import AsyncSessionLocal
from sqlalchemy import select
from src.models.contact import Contact


logger = logging.getLogger(__name__)

@celery_app.task(name="send_mailing_task")
async def send_mailing_task(mailing_subject: str, mailing_content: str):
    """
    Фоновая задача для рассылки писем.
    Использует синхронную обертку для запуска асинхронного кода внутри Celery.
    """
    return asyncio.run(run_mailing_process(mailing_subject, mailing_content))


async def run_mailing_process(subject: str, content: str):
    """Логика получения контактов из БД и 'отправки'"""

    async with AsyncSessionLocal() as db:
        # 1. Получаем все *активные* контакты
        query = select(Contact).where(Contact.is_active == True)
        result = await db.execute(query)
        contacts = result.scalars().all()
        
        logger.info(f"Начинаем рассылку: {subject}. Количество контактов: {len(contacts)}")

        # 2. Отправляем письма каждому
        for contact in contacts:
            # Здесь позже будет реальный код отправки через SMTP
            logger.info(f"Отправляем письмо {contact.email} | Контент: {content[:20]}...")

            # Небольшая пауза, чтобы имитировать сетевую задержку
            await asyncio.sleep(0.5)

        logger.info(f"Рассылка '{subject}' успешно завершена.")
        
        return f"Отправлено '{len(contacts)}' контактам"
    
