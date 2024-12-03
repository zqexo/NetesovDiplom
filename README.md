# Referral System

## Описание проекта

Referral System - это Django приложение, позволяющее реализовать систему реферальных ссылок и аутентификации по номеру телефона с использованием одноразовых кодов подтверждения.

---

## Структура проекта

```
netesovdiplom/
├── netesovdiplom/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
├── users/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   ├── utils.py
│   ├── views.py
│   ├── tests.py
├── frontend/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── forms.py
│   ├── urls.py
│   ├── views.py
│   ├── tests.py
├── .env
├── .env.docker
├── manage.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
```

- **app/**: Основное приложение с моделями, сериализаторами и API.
- **referral_system/**: Конфигурация проекта Django.
- **Dockerfile**: Описание образа для контейнера.
- **docker-compose.yml**: Настройка сервисов для контейнеризации.
- **requirements.txt**: Список зависимостей.

---

## Установка и запуск

### Требования
- Python 3.10+
- Docker и Docker Compose

### Шаги установки

1. Клонируйте репозиторий:
   ```bash
   git clone <URL_репозитория>
   cd referral_system
   ```

2. Установите зависимости (если запускаете локально):
   ```bash
   pip install -r requirements.txt
   ```

3. Запустите проект с помощью Docker:
   ```bash
   docker-compose up --build
   ```

4. Приложение будет доступно по адресу: `http://localhost:8000`

---

## Описание API

### Базовый URL
`http://localhost:8000`

### Эндпоинты

#### 1. **Отправка кода подтверждения**
**POST** `/auth/phone/`

**Описание:** Отправляет одноразовый код подтверждения на указанный номер телефона.

**Тело запроса:**
```json
{
  "phone": "<номер_телефона>"
}
```

**Ответ:**
- Успех:
  ```json
  {
    "message": "Code sent successfully"
  }
  ```
- Ошибка:
  ```json
  {
    "error": "Phone number is required"
  }
  ```

---

#### 2. **Проверка кода подтверждения**
**POST** `/auth/code/`

**Описание:** Проверяет одноразовый код и создаёт пользователя, если его не существует.
**ВАЖНО!** Телефон лучше указывать без + начиная с цифры 7, например (79991112233)

**Тело запроса:**
```json
{
  "phone": "<номер_телефона>",
  "code": "<код>"
}
```

**Ответ:**
- Успех:
  ```json
  {
    "message": "User created",
    "invite_code": "<реферальный_код>"
  }
  ```
- Ошибка:
  ```json
  {
    "error": "Invalid code"
  }
  ```

---

#### 3. **Просмотр профиля пользователя**
**GET** `/profile/?phone=<номер_телефона>`

**Описание:** Получает данные пользователя и список приглашённых.

**Ответ:**
- Успех:
  ```json
  {
    "phone": "<номер_телефона>",
    "invite_code": "<реферальный_код>",
    "invited_users": ["<номер_телефона>", ...]
  }
  ```
- Ошибка:
  ```json
  {
    "error": "User not found"
  }
  ```

---

#### 4. **Активация реферального кода**
**POST** `/profile/`

**Описание:** Активирует реферальный код для пользователя.

**Тело запроса:**
```json
{
  "phone": "<номер_телефона>",
  "invite_code": "<реферальный_код>"
}
```

**Ответ:**
- Успех:
  ```json
  {
    "message": "Referral activated"
  }
  ```
- Ошибка:
  ```json
  {
    "error": "Invalid phone or invite code"
  }
  ```

---

## Тестирование

1. Установите Postman.
2. Импортируйте коллекцию Postman из репозитория.
3. Выполните тестовые запросы к API.

---

## Docker команды

- Сборка контейнера:
  ```bash
  docker-compose build
  ```

- Запуск контейнеров:
  ```bash
  docker-compose up
  ```

- Остановка контейнеров:
  ```bash
  docker-compose down
  
