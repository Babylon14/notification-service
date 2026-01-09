import asyncio
import logging
import smtplib
from email.message import EmailMessage

from src.core.config import settings
from src.tasks.celery_app import celery_app
from src.database import AsyncSessionLocal
from sqlalchemy import select
from src.models.contact import Contact


logger = logging.getLogger(__name__)

async def run_mailing_process(subject: str, content: str) -> str:
    """Логика получения контактов из БД и 'отправки'"""

    async with AsyncSessionLocal() as db:
        # 1. Получаем все *активные* контакты
        query = select(Contact).where(Contact.is_active == True)
        result = await db.execute(query)
        contacts = result.scalars().all()

        if not contacts:
                return "Нет активных контактов"
        
        count = 0
        try:
            # Подключаемся к SMTP серверу
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                server.ehlo()
                if server.has_extn('STARTTLS'):
                    server.starttls() # Шифрование
                    server.ehlo()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            
                # 2. Отправляем письма каждому
                for contact in contacts:
                    try:
                        # Формируем письмо
                        msg = EmailMessage()
                        msg.set_content(content)
                        msg["Subject"] = subject
                        msg["From"] = "notification@service.com"
                        msg["To"] = contact.email

                        # Отправляем
                        server.send_message(msg)
                        count += 1
                        logger.info(f"Реальное письмо успешно отправлено на {contact.email}")
                    except Exception as err:
                        logger.error(f"Не удалось отправить письмо на {contact.email}: {err}")

        except Exception as err:
            logger.error(f"Критическая ошибка SMTP: {err}")
            return f"Ошибка SMTP: {err}"
        
        return f"Отправлено '{count}' реальных писем"
    

@celery_app.task(name="send_mailing_task")
def send_mailing_task(mailing_subject: str, mailing_content: str) -> str:
    """
    Точка входа Celery. Она запускает асинхронную логику.
    """
    try: 
        result = asyncio.run(run_mailing_process(mailing_subject, mailing_content))
        return result
    except Exception as err:
        logging.error(f"Ошибка при отправке рассылки: {err}")
        return str(err)
    
    
