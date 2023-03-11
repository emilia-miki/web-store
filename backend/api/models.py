from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)

class Product(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField()
    category = models.CharField(max_length=64)
    img = models.CharField(max_length=256)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    left = models.IntegerField()


class OrderStatus(models.IntegerChoices):
    Created = 0
    Sent = 1
    Received = 2
    Canceled = 3


class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    status = models.IntegerField(choices=OrderStatus.choices)
    date = models.DateTimeField(auto_now_add=True)


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.IntegerField()
