# Создать образ на основе базового слоя,
# который содержит файлы ОС и интерпретатор Python 3.9.
FROM python:3.9

# Установка зависимостей системы
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Установка рабочей директории
WORKDIR /app

# Копируем зависимости и устанавливаем
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копируем все файлы проекта
COPY . .

# Открываем порт
EXPOSE 8000

# Команда запуска сервера
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
