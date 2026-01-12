import enum
from datetime import datetime
from sqlalchemy import String, Text, DateTime, func, Enum
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class MailingStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    

class Mailing(Base):
    """Модель Рассылок"""
    __tablename__ = "mailings"

    id: Mapped[int] = mapped_column(primary_key=True)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<Рассылка(subject={self.subject})>"
    
