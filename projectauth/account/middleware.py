import jwt
from django.conf import settings
from .models import User


class JWTAuthMiddleware:
    """
    Читает заголовок Authorization: Bearer <token>,
    декодирует JWT и устанавливает request.user перед обработкой запроса.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.user = None
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ', 1)[1]
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                user = User.objects.select_related('role').get(
                    id=payload['user_id'],
                    is_active=True,
                )
                request.user = user
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, User.DoesNotExist):
                pass
        return self.get_response(request)
