import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import User


class JWTAuthentication(BaseAuthentication):
    """
    DRF authentication: читает заголовок Authorization: Bearer <token>,
    декодирует JWT и возвращает пользователя.
    """

    def authenticate(self, request):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return None  # не наш метод — DRF пробует следующий

        token = auth_header.split(' ', 1)[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Токен истёк.')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Недействительный токен.')

        try:
            user = User.objects.select_related('role').get(
                id=payload['user_id'],
                is_active=True,
            )
        except User.DoesNotExist:
            raise AuthenticationFailed('Пользователь не найден или деактивирован.')

        return (user, token)
