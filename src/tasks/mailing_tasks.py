import asyncio
import logging
import time
import smtplib
from email.message import EmailMessage

from src.core.config import settings
from src.tasks.celery_app import celery_app
from src.database import AsyncSessionLocal
from sqlalchemy import select, update

from src.models.contact import Contact
from src.models.mailing import Mailing, MailingStatus


logger = logging.getLogger(__name__)

async def run_mailing_process(mailing_id: int, subject: str, content: str) -> str:
    """Логика получения контактов из БД и 'отправки'"""

    async with AsyncSessionLocal() as db:
        # 1. Меняем статус на "В процессе"
        await db.execute(
            update(Mailing).where(Mailing.id == mailing_id).values(status=MailingStatus.PROCESSING)
        )
        await db.commit()

        # 2. Получаем все *активные* контакты
        query = select(Contact).where(Contact.is_active == True)
        result = await db.execute(query)
        contacts = result.scalars().all()

        if not contacts:
                return "Нет активных контактов"
        
        # 3. HTML-шаблон
        html_template = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <div style="background-color: #f4f4f4; padding: 20px; border-radius: 10px;">
                    <h2 style="color: #2c3e50;">{subject}</h2>
                    <p>{content}</p>
                    <hr>
                    <footer style="font-size: 12px; color: #777;">
                        Вы получили это письмо, так как подписаны на наши новости.
                    </footer>
                </div>
            </body>
        </html>
        """
        
        count = 0
        try:
            for contact in contacts:
                success = False
                attempts = 0
                while not success and attempts < 3:
                    try:
                        # Открываем соединение для КАЖДОГО контакта внутри его блока try
                        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                            server.ehlo()
                            if server.has_extn('STARTTLS'):
                                server.starttls()
                                server.ehlo()
                            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

                            # ОБРАБОТКА: Отправляем письмо
                            msg = EmailMessage()
                            msg["Subject"] = subject
                            msg["From"] = f"Сервис Рассылки <{settings.SMTP_USER}>"
                            msg["To"] = contact.email
                            msg.set_content(content) # СНАЧАЛА текст
                            msg.add_alternative(html_template, subtype="html") # ПОСЛЕ HTML

                            server.send_message(msg) # Отправляем
                            count += 1
                            success = True # Отправлено успешно!
                            logger.info(f"Реальное письмо успешно отправлено на {contact.email}")

                            # Увеличиваем паузу до 1.5 сек для стабильности
                            time.sleep(1.5)
                    except Exception as err:
                        attempts += 1
                        err_msg = str(err)
                        if "550" in err_msg:
                            logger.warning(f"Лимит достигнут на {contact.email}. Ждем 3 сек. Попытка {attempts}")
                            # Даем серверу "передохнуть" после ошибки лимита
                            time.sleep(3)
                        else:
                            logger.error(f"Не удалось отправить письмо на {contact.email}: {err}")
                            break
            # Если цикл дошел до конца без фатальных ошибок самого Python
            await db.execute(
                update(Mailing).where(Mailing.id == mailing_id).values(status=MailingStatus.COMPLETED)
            )
        except Exception as err:
            # Если упало что-то глобальное (например, БД)
            await db.execute(
                update(Mailing).where(Mailing.id == mailing_id).values(status=MailingStatus.FAILED)
            )
            logger.error(f"Критическая ошибка рассылки: {err}")
            
        await db.commit()
        return f"Отправлено '{count}' писем"
    

@celery_app.task(name="send_mailing_task")
def send_mailing_task(mailing_id: int, mailing_subject: str, mailing_content: str) -> str:
    """
    Точка входа Celery. Она запускает асинхронную логику.
    """
    try: 
        result = asyncio.run(run_mailing_process(mailing_id, mailing_subject, mailing_content))
        return result
    except Exception as err:
        logging.error(f"Ошибка при отправке рассылки: {err}")
        return str(err)
    
    
