import jwt
from datetime import datetime, timedelta
from django.conf import settings


def create_access_token(user_id: int) -> str:
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow(),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


def decode_access_token(token: str):
    return jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])