from django.urls import path
from . import views

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('token/', TokenObtainPairView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
    path('register/', views.register),
    path('account/', views.account),
    path('change_password/', views.change_password),
    path("products/", views.products),
    path("products/<str:pk>/", views.product),
    path("orders/", views.orders),
    path("orders/<str:pk>/", views.order),
    path("categories/", views.categories),
    path("generate_orders/", views.generate_orders),
]
