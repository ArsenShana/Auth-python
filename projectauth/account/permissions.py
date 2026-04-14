from rest_framework.permissions import BasePermission
from .models import AccessRule


class IsAuthenticated(BasePermission):
    """Пользователь должен быть авторизован (request.user установлен)."""

    message = "Необходима авторизация."

    def has_permission(self, request, view):
        return request.user is not None


class IsAdmin(BasePermission):
    """Пользователь должен иметь роль admin."""

    message = "Доступ разрешён только администраторам."

    def has_permission(self, request, view):
        return request.user is not None and request.user.role.name == 'admin'


class HasElementAccess(BasePermission):
    """
    Проверяет права доступа к бизнес-элементу.
    View должен определить атрибуты:
      - element_code: str  — код бизнес-элемента
      - required_permission: str — 'can_read' | 'can_create' | 'can_update' | 'can_delete'
    """

    message = "У вас нет доступа к этому ресурсу."

    def has_permission(self, request, view):
        if request.user is None:
            return False
        element_code = getattr(view, 'element_code', None)
        required = getattr(view, 'required_permission', 'can_read')
        if not element_code:
            return True
        try:
            rule = AccessRule.objects.get(
                role=request.user.role,
                element__code=element_code,
            )
            return getattr(rule, required, False)
        except AccessRule.DoesNotExist:
            return False
