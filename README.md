# Auth System

Бэкенд-приложение с кастомной системой аутентификации и авторизации на Django + DRF.

## Стек технологий

| Технология | Назначение |
|---|---|
| Django 6 + DRF | Основной фреймворк и API |
| PostgreSQL 16 | База данных (запускается через Docker) |
| bcrypt | Хэширование паролей |
| PyJWT | JWT токены (алгоритм HS256, срок 24 часа) |
| Docker | Контейнер для PostgreSQL |

---

## Быстрый запуск

```bash
# 1. Клонировать репозиторий
git clone https://github.com/ArsenShana/Auth-python.git
cd Auth-python/projectauth

# 2. Создать виртуальное окружение
python3 -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt

# 3. Поднять PostgreSQL
cd .. && docker compose up -d && cd projectauth

# 4. Применить миграции и загрузить тестовые данные
python manage.py migrate
python manage.py loaddata account/fixtures/initial_data.json
python manage.py seed_users

# 5. Запустить сервер
python manage.py runserver 0.0.0.0:8000
```

После запуска открыть в браузере: **http://localhost:8000/**

---

## Веб-интерфейс

| Страница | URL | Описание |
|---|---|---|
| Вход | `/login/` | Авторизация по email и паролю |
| Регистрация | `/register/` | Создание нового аккаунта |
| Дашборд | `/dashboard/` | Профиль, JWT токен, таблица прав (для admin) |
| Каталог | `/catalog/` | Товары, магазины, заказы — проверка прав доступа |

---

## Схема базы данных

### Роли (`account_role`)

| Поле | Тип | Описание |
|---|---|---|
| id | PK | |
| name | varchar(50) | admin / manager / user / guest |
| description | text | Описание роли |

### Пользователи (`account_user`)

| Поле | Тип | Описание |
|---|---|---|
| id | PK | |
| first_name | varchar(100) | Имя |
| last_name | varchar(100) | Фамилия |
| middle_name | varchar(100) | Отчество (необязательно) |
| email | varchar | Уникальный, используется для входа |
| password_hash | varchar(255) | bcrypt хэш пароля |
| role_id | FK → Role | Роль пользователя |
| is_active | bool | false = мягко удалён, вход заблокирован |
| created_at | datetime | Дата регистрации |
| updated_at | datetime | Дата последнего обновления |

### Бизнес-объекты (`account_businesselement`)

| Поле | Тип | Описание |
|---|---|---|
| id | PK | |
| code | varchar(100) | Уникальный код: users, products, shops, orders, rules |
| name | varchar(100) | Название |
| description | text | Описание |

### Правила доступа (`account_accessrule`)

| Поле | Тип | Описание |
|---|---|---|
| id | PK | |
| role_id | FK → Role | Роль |
| element_id | FK → BusinessElement | Бизнес-объект |
| can_read | bool | Чтение своих объектов |
| can_read_all | bool | Чтение всех объектов |
| can_create | bool | Создание |
| can_update | bool | Изменение своих объектов |
| can_update_all | bool | Изменение всех объектов |
| can_delete | bool | Удаление своих объектов |
| can_delete_all | bool | Удаление всех объектов |

> Пара `(role_id, element_id)` уникальна.

---

## Матрица прав доступа

| Роль | users | products | shops | orders | rules |
|---|---|---|---|---|---|
| admin | CRUD all | CRUD all | CRUD all | CRUD all | CRUD all |
| manager | чтение/изм. своих | CRUD all | чтение/изм. своих | CRUD all | нет |
| user | чтение/изм. своих | чтение | чтение | чтение своих, создание | нет |
| guest | нет | чтение | чтение | нет | нет |

---

## Как работает аутентификация

1. При регистрации пароль хэшируется через **bcrypt** и сохраняется в `password_hash`
2. При входе `bcrypt.checkpw()` сравнивает пароль с хэшем
3. После успешного входа сервер создаёт **JWT токен** с `user_id` и сроком действия 24 часа
4. Клиент передаёт токен в каждом запросе: `Authorization: Bearer <token>`
5. `JWTAuthentication` (DRF класс) декодирует токен и устанавливает `request.user`
6. Если токен истёк или недействителен — возвращается **401 Unauthorized**
7. Мягкое удаление: `is_active = False` — запись остаётся в БД, вход заблокирован

---

## API эндпоинты

### Аутентификация

| Метод | URL | Описание | Доступ |
|---|---|---|---|
| POST | `/api/auth/register/` | Регистрация нового пользователя | Публичный |
| POST | `/api/auth/login/` | Вход, возвращает JWT токен | Публичный |
| POST | `/api/auth/logout/` | Выход из системы | Авторизован |
| GET | `/api/auth/profile/` | Получить данные профиля | Авторизован |
| PATCH | `/api/auth/profile/` | Обновить профиль или пароль | Авторизован |
| DELETE | `/api/auth/profile/` | Мягкое удаление аккаунта | Авторизован |

### Управление правами (только admin)

| Метод | URL | Описание |
|---|---|---|
| GET | `/api/access-rules/` | Список всех правил доступа |
| POST | `/api/access-rules/` | Создать правило |
| GET | `/api/access-rules/<id>/` | Получить одно правило |
| PATCH | `/api/access-rules/<id>/` | Изменить правило |
| DELETE | `/api/access-rules/<id>/` | Удалить правило |
| GET | `/api/roles/` | Список ролей |
| GET | `/api/elements/` | Список бизнес-объектов |

### Mock бизнес-объекты

| Метод | URL | Необходимое право |
|---|---|---|
| GET | `/api/products/` | `can_read` на products |
| GET | `/api/shops/` | `can_read` на shops |
| GET | `/api/orders/` | `can_read` на orders |

---

## Тестовые пользователи

| Email | Пароль | Роль |
|---|---|---|
| admin@example.com | admin123 | admin |
| manager@example.com | manager123 | manager |
| user@example.com | user123 | user |
| guest@example.com | guest123 | guest |

---

## Структура проекта

```
projectauth/
├── account/
│   ├── models.py                        # User, Role, BusinessElement, AccessRule
│   ├── authentication.py                # DRF JWTAuthentication класс
│   ├── middleware.py                    # JWTAuthMiddleware
│   ├── permissions.py                   # IsAuthenticated, IsAdmin, HasElementAccess
│   ├── serializers.py                   # Сериализаторы для всех endpoints
│   ├── views.py                         # API views + Django template views
│   ├── urls.py                          # Маршруты
│   ├── jwt_utils.py                     # Создание и декодирование JWT
│   ├── fixtures/initial_data.json       # Роли, элементы, правила доступа
│   ├── management/commands/seed_users.py# Команда создания тестовых пользователей
│   └── templates/account/               # HTML шаблоны (login, register, dashboard, catalog)
├── projectauth/
│   ├── settings.py
│   └── urls.py
└── manage.py
docker-compose.yml                       # PostgreSQL 16
requirements.txt
```
