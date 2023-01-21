from django.db import models
from django.contrib.auth.models import User


class Product(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField()
    category = models.CharField(max_length=64)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    left = models.IntegerField()


class OrderStatus(models.IntegerChoices):
    Created = 0
    Paid = 1
    Sent = 2
    Finished = 3
    Canceled = 4


class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.IntegerField(choices=OrderStatus.choices)


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.IntegerField()
