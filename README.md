# Auth System — Тестовое задание

## Стек технологий
- **Django 6 + DRF** — backend framework
- **PostgreSQL 16** — база данных (в Docker)
- **bcrypt** — хэширование паролей
- **PyJWT** — JWT токены (HS256, TTL 24ч)

---

## Схема базы данных

### `account_role` — Роли пользователей
| Поле        | Тип          | Описание         |
|-------------|--------------|------------------|
| id          | PK           |                  |
| name        | varchar(50)  | admin / manager / user / guest |
| description | text         |                  |

### `account_user` — Пользователи
| Поле          | Тип          | Описание                          |
|---------------|--------------|-----------------------------------|
| id            | PK           |                                   |
| first_name    | varchar(100) | Имя                               |
| last_name     | varchar(100) | Фамилия                           |
| middle_name   | varchar(100) | Отчество (необязательно)          |
| email         | varchar      | Уникальный, используется для входа|
| password_hash | varchar(255) | bcrypt хэш пароля                 |
| role_id       | FK → Role    | Роль пользователя                 |
| is_active     | bool         | False = мягко удалён              |
| created_at    | datetime     |                                   |
| updated_at    | datetime     |                                   |

### `account_businesselement` — Бизнес-объекты системы
| Поле        | Тип         | Описание                        |
|-------------|-------------|---------------------------------|
| id          | PK          |                                 |
| code        | varchar(100)| Уникальный код (users, products…)|
| name        | varchar(100)| Название                        |
| description | text        |                                 |

### `account_accessrule` — Правила доступа (ACL)
| Поле            | Тип            | Описание                         |
|-----------------|----------------|----------------------------------|
| id              | PK             |                                  |
| role_id         | FK → Role      |                                  |
| element_id      | FK → BusinessElement |                            |
| can_read        | bool           | Чтение своих объектов            |
| can_read_all    | bool           | Чтение всех объектов             |
| can_create      | bool           | Создание                         |
| can_update      | bool           | Изменение своих объектов         |
| can_update_all  | bool           | Изменение всех объектов          |
| can_delete      | bool           | Удаление своих объектов          |
| can_delete_all  | bool           | Удаление всех объектов           |

> Уникальность: пара `(role_id, element_id)`.

---

## Матрица прав доступа

| Роль    | users           | products        | shops      | orders          | rules |
|---------|-----------------|-----------------|------------|-----------------|-------|
| admin   | CRUD all        | CRUD all        | CRUD all   | CRUD all        | CRUD all |
| manager | read own, update own | CRUD all   | read, update own | CRUD all  | нет |
| user    | read own, update own | read all   | read all   | read own, create | нет |
| guest   | нет             | read all        | read all   | нет             | нет |

---

## Аутентификация

1. Пароль хэшируется через **bcrypt** перед сохранением в БД.
2. После login сервер создаёт **JWT токен** (payload: `user_id`, `exp`, `iat`).
3. Клиент передаёт токен в заголовке: `Authorization: Bearer <token>`.
4. **JWTAuthMiddleware** декодирует токен при каждом запросе и устанавливает `request.user`.
5. Если токен истёк или некорректен — `request.user = None` → 401.

---

## API эндпоинты

### Аутентификация
| Метод | URL                  | Описание              | Доступ |
|-------|----------------------|-----------------------|--------|
| POST  | /api/auth/register/  | Регистрация           | Public |
| POST  | /api/auth/login/     | Вход                  | Public |
| POST  | /api/auth/logout/    | Выход                 | Auth   |
| GET   | /api/auth/profile/   | Профиль               | Auth   |
| PATCH | /api/auth/profile/   | Обновление профиля    | Auth   |
| DELETE| /api/auth/profile/   | Мягкое удаление       | Auth   |

### Управление правилами (только admin)
| Метод | URL                       | Описание           |
|-------|---------------------------|--------------------|
| GET   | /api/access-rules/        | Список правил      |
| POST  | /api/access-rules/        | Создать правило    |
| GET   | /api/access-rules/<id>/   | Одно правило       |
| PATCH | /api/access-rules/<id>/   | Изменить правило   |
| DELETE| /api/access-rules/<id>/   | Удалить правило    |
| GET   | /api/roles/               | Список ролей       |
| GET   | /api/elements/            | Список элементов   |

### Mock бизнес-объекты
| Метод | URL            | Доступ               |
|-------|----------------|----------------------|
| GET   | /api/products/ | can_read на products |
| GET   | /api/shops/    | can_read на shops    |
| GET   | /api/orders/   | can_read на orders   |

---

## Тестовые пользователи

| Email                | Пароль     | Роль    |
|----------------------|------------|---------|
| admin@example.com    | admin123   | admin   |
| manager@example.com  | manager123 | manager |
| user@example.com     | user123    | user    |
| guest@example.com    | guest123   | guest   |

---

## Запуск

```bash
# 1. Поднять Postgres
docker compose up -d

# 2. Активировать venv
source venv/bin/activate

# 3. Применить миграции
cd projectauth
python manage.py migrate

# 4. Загрузить данные
python manage.py loaddata account/fixtures/initial_data.json
python manage.py seed_users

# 5. Запустить сервер
python manage.py runserver
```
