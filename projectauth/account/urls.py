from django.urls import path
from .views import (
    RegisterView, LoginView, LogoutView, ProfileView,
    AccessRuleListCreateView, AccessRuleDetailView,
    RoleListView, BusinessElementListView,
    ProductListView, ShopListView, OrderListView,
)

urlpatterns = [
    # Auth
    path('auth/register/', RegisterView.as_view()),
    path('auth/login/',    LoginView.as_view()),
    path('auth/logout/',   LogoutView.as_view()),
    path('auth/profile/',  ProfileView.as_view()),

    # Access rules management (admin only)
    path('access-rules/',      AccessRuleListCreateView.as_view()),
    path('access-rules/<int:pk>/', AccessRuleDetailView.as_view()),
    path('roles/',             RoleListView.as_view()),
    path('elements/',          BusinessElementListView.as_view()),

    # Mock business objects
    path('products/', ProductListView.as_view()),
    path('shops/',    ShopListView.as_view()),
    path('orders/',   OrderListView.as_view()),
]
