import bcrypt
from django.core.management.base import BaseCommand
from account.models import User, Role


SEED_USERS = [
    {"first_name": "Арсен",   "last_name": "Админов",   "middle_name": "Иванович", "email": "admin@example.com",   "password": "admin123",   "role": "admin"},
    {"first_name": "Мария",   "last_name": "Менеджерова","middle_name": "",         "email": "manager@example.com", "password": "manager123", "role": "manager"},
    {"first_name": "Иван",    "last_name": "Пользов",   "middle_name": "Петрович", "email": "user@example.com",    "password": "user123",    "role": "user"},
    {"first_name": "Гость",   "last_name": "Гостев",    "middle_name": "",         "email": "guest@example.com",   "password": "guest123",   "role": "guest"},
]


class Command(BaseCommand):
    help = "Создаёт тестовых пользователей"

    def handle(self, *args, **kwargs):
        for data in SEED_USERS:
            if User.objects.filter(email=data['email']).exists():
                self.stdout.write(f"  уже существует: {data['email']}")
                continue
            role = Role.objects.get(name=data['role'])
            password_hash = bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt()).decode()
            User.objects.create(
                first_name=data['first_name'],
                last_name=data['last_name'],
                middle_name=data['middle_name'],
                email=data['email'],
                password_hash=password_hash,
                role=role,
            )
            self.stdout.write(self.style.SUCCESS(f"  создан: {data['email']} (роль: {data['role']})"))
