from rest_framework.serializers import ModelSerializer
from .models import Product, Order


class ProductSerializer(ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class OrderSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = "__all__"
