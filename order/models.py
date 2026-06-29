from enum import Enum

from django.db import models

class OrderDetails(models.Model):
    book = models.ForeignKey('shop.Book',on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10,decimal_places=2)
    amount = models.IntegerField()
    order = models.ForeignKey('Order',on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.book.title}, {self.amount}, {self.order.id}'


class OrderStatus(Enum):
    PENDING = 'PENDING'
    PROCESSING = 'PROCESSING'
    SHIPPED = 'SHIPPED'
    DELIVERED = 'DELIVERED'
    CANCELED = 'CANCELED'

class PaymentStatus(Enum):
    PENDING = 'PENDING'
    PROCESSING = 'PROCESSING'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'


class Order(models.Model):
    owner = models.ForeignKey('auth.User',on_delete=models.CASCADE)
    delivery_address = models.ForeignKey('user_management.DeliveryAddress',on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10,decimal_places=2)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=20)
    ttn = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.id} {self.owner} {self.created_at}'