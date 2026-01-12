import asyncio
import logging
import smtplib
from email.message import EmailMessage

from src.core.config import settings
from src.tasks.celery_app import celery_app
from src.database import AsyncSessionLocal
from sqlalchemy import select, update

from src.models.contact import Contact
from src.models.mailing import Mailing, MailingStatus


logger = logging.getLogger(__name__)

@celery_app.task(
        bind=True,                      # привязка к текущему контексту
        name="send_single_email_task",  # название задачи
        max_retries=5,                  # максимум 5 попыток
        default_retry_delay=5,          # если упал, попробуй через 5 сек
)
def send_single_email_task(self, email: str, subject: str, content: str, html_content: str) -> str:
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

            # ОБРАБОТКА: Отправляем письмо
            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = f"Сервис Рассылки <{settings.SMTP_USER}>"
            msg["To"] = email
            msg.set_content(content) # СНАЧАЛА текст
            msg.add_alternative(html_content, subtype="html") # ПОСЛЕ HTML

            server.send_message(msg) # Отправляем
            return f"Письмо отправлено {email}"
        
    except Exception as exc:
        # Если это лимит Mailtrap, отправляем задачу на повтор
        if "550" in str(exc):
            raise self.retry(exc=exc, countdown=5) # запускаем через 5 секунд
        logger.error(f"Ошибка при отправке письма для {email}: {exc}")
        raise exc


@celery_app.task(name="start_mailing_orchestrator")
def start_mailing_orchestrator(mailing_id: int, subject: str, content: str):
    """Основная логика рассылки, готовит данные и раздает команды."""
    try:
        return asyncio.run(_orchestrate(mailing_id, subject, content))
    except Exception as err:
        logger.error(f"Критический сбой оркестратора: {err}")
        return str(err)


async def _orchestrate(mailing_id: int, subject: str, content: str):
    async with AsyncSessionLocal() as db:
        # 1. Ставим статус PROCESSING
        await db.execute(
            update(Mailing).where(Mailing.id == mailing_id).values(status=MailingStatus.PROCESSING)
        )
        await db.commit()
        
        # 2. Получаем *активные* контакты
        result = await db.execute(
            select(Contact).where(Contact.is_active == True)
        )
        contacts = result.scalars().all()

        logger.info(f"Оркестратор нашел {len(contacts)} активных контактов для рассылки #{mailing_id}")

        if not contacts:
                return "Нет активных контактов"
        
        # 3. Генерируем шаблон
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

        # 4. Вместо цикла с отправкой, мы создаем задачи
        for contact in contacts:
            logger.info(f"Создаю задачу для {contact.email}")
            # Кидаем задачу в очередь и идем дальше.
            send_single_email_task.delay(
                email=contact.email,
                subject=subject,
                content=content,
                html_content=html_template
            )
        # 5. Сразу ставим COMPLETED, потому что задачи уже в очереди
        await db.execute(
            update(Mailing).where(Mailing.id == mailing_id).values(status=MailingStatus.COMPLETED)
        )
        await db.commit()
        return f"Запущена рассылка для {len(contacts)} адресатов"
    

@celery_app.task(name="send_mailing_task")
def send_mailing_task(mailing_id: int, mailing_subject: str, mailing_content: str) -> str:
    """
    Точка входа Celery. Она запускает асинхронную логику.
    """
    try: 
        result = asyncio.run(start_mailing_orchestrator(mailing_id, mailing_subject, mailing_content))
        return result
    except Exception as err:
        logging.error(f"Ошибка при отправке рассылки: {err}")
        return str(err)
    
    
