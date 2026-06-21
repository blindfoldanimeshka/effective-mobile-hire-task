# API контроля доступа

Backend API-сервис для управления доступом пользователей к бизнес-ресурсам с использованием ролей и правил доступа.

## Технологический стек

- Python 3.11+ / Django 4.2+ / Django REST Framework
- PostgreSQL
- JWT-аутентификация (djangorestframework-simplejwt)
- Хеширование паролей с помощью bcrypt

## Схема базы данных

### Таблицы

1. **User** — пользовательская модель (UUID PK, email как логин, пароль через bcrypt, поле is_active для мягкого удаления)
2. **Role** — справочная таблица (admin, manager, viewer)
3. **UserRole** — связывает пользователей с ролями (одна роль на пользователя)
4. **BusinessElement** — демо-бизнес-ресурсы (article, product, order)
5. **AccessRule** — матрица прав доступа: роль × элемент → can_read, can_create, can_update, can_delete

### Как работают разрешения

```
User → UserRole → Role → AccessRule → BusinessElement
                                    → can_read / can_create / can_update / can_delete
```

Когда пользователь запрашивает бизнес-элемент, система:
1. Находит роль пользователя через UserRole
2. Ищет AccessRule для данной роли и элемента
3. Проверяет соответствующий флаг разрешения

## Установка

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create PostgreSQL database
createdb mobile_effective

# 4. Set environment variables (optional, defaults work for local dev)
export DB_NAME=mobile_effective
export DB_USER=postgres
export DB_PASSWORD=postgres

# 5. Run migrations
python manage.py migrate

# 6. Seed test data
python manage.py seed_data

# 7. Start server
python manage.py runserver
```

## Тестовые пользователи

| Электронная почта | Пароль | Роль |
|-------|----------|------|
| admin@example.com | admin123 | admin (полный CRUD для всех элементов) |
| manager@example.com | manager123 | manager (чтение + создание + обновление) |
| viewer@example.com | viewer123 | viewer (только чтение) |

## API-эндпоинты

### Аутентификация (без токена)
- `POST /api/auth/register/` — регистрация
- `POST /api/auth/login/` — вход, возвращает JWT-токены
- `POST /api/auth/refresh/` — обновление токена доступа

### Профиль (требуется токен)
- `GET /api/profile/` — получить профиль
- `PATCH /api/profile/` — обновить профиль
- `DELETE /api/profile/` — мягкое удаление (деактивация аккаунта)

### Админ (токен + роль admin)
- `GET /api/admin/roles/` — список ролей
- `POST /api/admin/roles/` — создать роль
- `GET /api/admin/access-rules/` — список правил доступа
- `POST /api/admin/access-rules/` — создать правило доступа
- `PUT /api/admin/access-rules/{id}/` — обновить правило доступа
- `DELETE /api/admin/access-rules/{id}/` — удалить правило доступа
- `POST /api/admin/users/{id}/role/` — назначить роль пользователю

### Бизнес-элементы (токен + проверка доступа)
- `GET /api/business-elements/` — список (требуется can_read)
- `POST /api/business-elements/` — создание (требуется can_create)
- `GET /api/business-elements/{id}/` — детали (требуется can_read)
- `PUT /api/business-elements/{id}/` — обновление (требуется can_update)
- `DELETE /api/business-elements/{id}/` — удаление (требуется can_delete)

## Примеры запросов

### Регистрация
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"new@example.com","first_name":"John","last_name":"Doe","password":"pass123","password_confirm":"pass123"}'
```

### Вход
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}'
```

### Доступ к бизнес-элементу (с токеном)
```bash
curl http://localhost:8000/api/business-elements/ \
  -H "Authorization: Bearer <your_token>"
```

## Коды ошибок

| Код | Описание |
|------|---------|
| 400 | Неверный запрос / ошибка валидации |
| 401 | Не аутентифицирован или неактивный пользователь |
| 403 | Аутентифицирован, но нет разрешения |
| 404 | Ресурс не найден |
| 409 | Конфlict (например, дублирующаяся электронная почта) |
