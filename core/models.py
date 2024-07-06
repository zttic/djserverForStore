from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.models import User


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, help_text="Enter a product name", unique=True)
    # price = models.DecimalField(
    #     max_digits=10, decimal_places=2, help_text="Enter a product price")
    unit = models.CharField(max_length=100, help_text="Enter a product unit")
    # productId = models.AutoField(primary_key=True)
    imgurl = models.CharField(default="", max_length=200, help_text="Enter a product imgurl")
    level = models.IntegerField(default=1, help_text="Enter a product level")
    isShow = models.BooleanField(default=True, help_text="Enter a product isShow")
    categoryId = models.IntegerField(default=1, help_text="Enter a product categoryId")


class ItemofProduct(models.Model):
    id = models.AutoField(primary_key=True)
    productId = models.ForeignKey(Product, related_name='item', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    imgurl = models.CharField(default="", max_length=200)
    description = models.TextField(default="")
    available = models.BooleanField(default=True)
    sortOrder = models.IntegerField(default=1)


class Gallery(models.Model):
    id = models.AutoField(primary_key=True)
    imgurl = models.CharField(max_length=200)
    productId = models.ForeignKey(
        Product, related_name='gallery', on_delete=models.CASCADE)


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    userId = models.IntegerField()
    date = models.DateTimeField(default=timezone.now)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_quantity = models.IntegerField(default=0)
    status = models.IntegerField(default=1)
    payMethod = models.IntegerField()

class OrderItem(models.Model):
    id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=200, default="")
    item_name = models.CharField(max_length=200, default="")
    orderId = models.ForeignKey(Order, related_name='orderItem', on_delete=models.CASCADE)
    productId = models.ForeignKey(Product, related_name='orderItem', on_delete=models.CASCADE)
    itemId = models.ForeignKey(ItemofProduct, related_name='orderItem', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(default="")
    isShow = models.BooleanField(default=True)
    sortOrder = models.IntegerField(default=1)

class Test(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)


class Unit(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    isShow = models.BooleanField(default=True)
    sortOrder = models.IntegerField(default=1)

class Cart(models.Model):
    id = models.AutoField(primary_key=True)
    userId = models.IntegerField()
    productId = models.IntegerField()
    itemId = models.IntegerField()
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(default=timezone.now)
    selected = models.BooleanField(default=True)

class Address(models.Model):
    id = models.AutoField(primary_key=True)
    userId = models.IntegerField()
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=200)
    isDefault = models.BooleanField(default=False)
    isShow = models.BooleanField(default=True)
    sortOrder = models.IntegerField(default=1)


# class User(models.Model):
#     id = models.AutoField(primary_key=True)
#     username = models.CharField(max_length=100, default="")
#     password = models.CharField(max_length=100, default="")
#     last_login = models.DateTimeField(default=timezone.now)
#     is_active = models.BooleanField(default=True)
#     # sortOrder = models.IntegerField(default=1)
#     level = models.IntegerField(default=1) # 1是未授权，2是已授权


class Customer(models.Model):
    # id = models.AutoField(primary_key=True)
    # username = models.CharField(max_length=100, default="")
    # date_joined = models.DateTimeField(default=timezone.now)
    # last_login = models.DateTimeField(default=timezone.now)
    # is_active = models.BooleanField(default=True)
    # # sortOrder = models.IntegerField(default=1)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='for_customer')
    level = models.IntegerField(default=1)  # 1是未授权，2是已授权
    phone_number = models.CharField(max_length=20, unique=True)
