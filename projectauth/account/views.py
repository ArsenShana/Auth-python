import bcrypt
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import User, AccessRule, BusinessElement, Role
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    ProfileUpdateSerializer, AccessRuleSerializer,
    RoleSerializer, BusinessElementSerializer,
)
from .jwt_utils import create_access_token
from .permissions import IsAuthenticated, IsAdmin, HasElementAccess


# ── Auth ──────────────────────────────────────────────────────────────────────

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        token = create_access_token(user.id)
        return Response(
            {"message": "Регистрация успешна.", "token": token, "user": UserSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = User.objects.select_related('role').get(email=email)
        except User.DoesNotExist:
            return Response({"error": "Неверный email или пароль."}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({"error": "Аккаунт деактивирован."}, status=status.HTTP_401_UNAUTHORIZED)

        if not bcrypt.checkpw(password.encode(), user.password_hash.encode()):
            return Response({"error": "Неверный email или пароль."}, status=status.HTTP_401_UNAUTHORIZED)

        token = create_access_token(user.id)
        return Response({"token": token, "user": UserSerializer(user).data})


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # JWT stateless: клиент удаляет токен.
        # При необходимости здесь можно добавить blacklist токенов.
        return Response({"message": "Выход выполнен успешно."})


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        serializer = ProfileUpdateSerializer(
            request.user, data=request.data, partial=True, context={'request': request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        return Response({"message": "Профиль обновлён.", "user": UserSerializer(user).data})

    def delete(self, request):
        # Мягкое удаление: is_active=False
        user = request.user
        user.is_active = False
        user.save()
        return Response({"message": "Аккаунт деактивирован."}, status=status.HTTP_200_OK)


# ── Access Rules (admin only) ─────────────────────────────────────────────────

class AccessRuleListCreateView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        rules = AccessRule.objects.select_related('role', 'element').all()
        return Response(AccessRuleSerializer(rules, many=True).data)

    def post(self, request):
        serializer = AccessRuleSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        rule = serializer.save()
        return Response(AccessRuleSerializer(rule).data, status=status.HTTP_201_CREATED)


class AccessRuleDetailView(APIView):
    permission_classes = [IsAdmin]

    def _get_rule(self, pk):
        try:
            return AccessRule.objects.select_related('role', 'element').get(pk=pk)
        except AccessRule.DoesNotExist:
            return None

    def get(self, request, pk):
        rule = self._get_rule(pk)
        if not rule:
            return Response({"error": "Правило не найдено."}, status=status.HTTP_404_NOT_FOUND)
        return Response(AccessRuleSerializer(rule).data)

    def patch(self, request, pk):
        rule = self._get_rule(pk)
        if not rule:
            return Response({"error": "Правило не найдено."}, status=status.HTTP_404_NOT_FOUND)
        serializer = AccessRuleSerializer(rule, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        rule = serializer.save()
        return Response(AccessRuleSerializer(rule).data)

    def delete(self, request, pk):
        rule = self._get_rule(pk)
        if not rule:
            return Response({"error": "Правило не найдено."}, status=status.HTTP_404_NOT_FOUND)
        rule.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RoleListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        return Response(RoleSerializer(Role.objects.all(), many=True).data)


class BusinessElementListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        return Response(BusinessElementSerializer(BusinessElement.objects.all(), many=True).data)


# ── Mock Business Objects ─────────────────────────────────────────────────────

MOCK_PRODUCTS = [
    {"id": 1, "name": "Ноутбук Dell XPS 15", "price": 450000, "category": "Электроника"},
    {"id": 2, "name": "Смартфон Samsung Galaxy S24", "price": 250000, "category": "Электроника"},
    {"id": 3, "name": "Кресло офисное Herman Miller", "price": 180000, "category": "Мебель"},
    {"id": 4, "name": "Монитор LG 27\"", "price": 120000, "category": "Электроника"},
    {"id": 5, "name": "Клавиатура механическая Keychron", "price": 45000, "category": "Аксессуары"},
]

MOCK_SHOPS = [
    {"id": 1, "name": "TechStore Алматы", "city": "Алматы", "address": "пр. Абая, 10"},
    {"id": 2, "name": "TechStore Астана",  "city": "Астана",  "address": "пр. Республики, 25"},
    {"id": 3, "name": "TechStore Шымкент", "city": "Шымкент", "address": "ул. Байтурсынова, 5"},
]

MOCK_ORDERS = [
    {"id": 1, "product": "Ноутбук Dell XPS 15", "customer": "Иван Иванов", "status": "completed", "amount": 450000},
    {"id": 2, "product": "Смартфон Samsung",    "customer": "Мария Сидорова", "status": "pending",   "amount": 250000},
    {"id": 3, "product": "Монитор LG 27\"",     "customer": "Алексей Петров", "status": "shipped",   "amount": 120000},
]


class ProductListView(APIView):
    permission_classes = [IsAuthenticated, HasElementAccess]
    element_code = 'products'
    required_permission = 'can_read'

    def get(self, request):
        return Response(MOCK_PRODUCTS)


class ShopListView(APIView):
    permission_classes = [IsAuthenticated, HasElementAccess]
    element_code = 'shops'
    required_permission = 'can_read'

    def get(self, request):
        return Response(MOCK_SHOPS)


class OrderListView(APIView):
    permission_classes = [IsAuthenticated, HasElementAccess]
    element_code = 'orders'
    required_permission = 'can_read'

    def get(self, request):
        return Response(MOCK_ORDERS)


# ── Template Views ────────────────────────────────────────────────────────────

def page_login(request):
    return render(request, 'account/login.html')

def page_register(request):
    return render(request, 'account/register.html')

def page_dashboard(request):
    return render(request, 'account/dashboard.html')

def page_catalog(request):
    return render(request, 'account/catalog.html')
