from django.urls import path, include
from . import views

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')),
    path("products/", views.products),
    path("products/<str:pk>/", views.product),
    path("orders/", views.orders),
    path("orders/<str:pk>/", views.order),
]
