# Используем легковесный образ Python
FROM python:3.11-slim

# Устанавливаем переменные окружения, чтобы Python не создавал .pyc файлы 
# и сразу выводил логи в консоль (без буферизации)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости (необходимы для asyncpg и других библиотек)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Сначала копируем только файл с зависимостями, чтобы Docker кэшировал этот слой
COPY requirements.txt .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем весь код проекта в контейнер
COPY . .

# Код запускается через команды в docker-compose.yml