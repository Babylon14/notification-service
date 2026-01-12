"""add_status_to_mailing

Revision ID: ac4d03fdfae6
Revises: 58bed09d008e
Create Date: 2026-01-12 09:38:20.131109

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
# Добавляем импорт диалекта Postgres
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'ac4d03fdfae6'
down_revision: Union[str, Sequence[str], None] = '58bed09d008e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Сначала создаем сам тип ENUM в базе данных
    mailing_status = postgresql.ENUM('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', name='mailingstatus')
    mailing_status.create(op.get_bind())

    # 2. Добавляем колонку как допускающую NULL (удаляем nullable=False)
    op.add_column('mailings', sa.Column('status', sa.Enum('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', name='mailingstatus'), nullable=True))

    # 3. Устанавливаем статус PENDING для всех старых записей, где он пустой
    op.execute("UPDATE mailings SET status = 'PENDING' WHERE status IS NULL")

    # 4. Теперь делаем колонку обязательной (NOT NULL)
    op.alter_column('mailings', 'status', nullable=False)
    

def downgrade() -> None:
    # 1. Сначала удаляем колонку
    op.drop_column('mailings', 'status')

    # 2. Затем удаляем сам тип ENUM из базы
    mailing_status = postgresql.ENUM('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', name='mailingstatus')
    mailing_status.drop(op.get_bind())

