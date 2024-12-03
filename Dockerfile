FROM python:3.11-slim

WORKDIR /code

RUN pip install --upgrade pip

# Копирование requirements.txt и установка зависимостей
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# Копирование остальных файлов
COPY . .

# Установка точки входа
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]