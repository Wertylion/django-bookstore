from django.db import models


class OrderStatus(models.TextChoices):

    PENDING = 'PENDING', 'Очікує'
    PROCESSING = 'PROCESSING', 'В обробці'
    SHIPPED = 'SHIPPED', 'Відправлено'
    DELIVERED = 'DELIVERED', 'Доставлено'
    CANCELED = 'CANCELED', 'Скасовано'


class PaymentStatus(models.TextChoices):
    PENDING = 'PENDING', 'Очікує'
    PROCESSING = 'PROCESSING', 'В обробці'
    COMPLETED = 'COMPLETED', 'Завершено'
    FAILED = 'FAILED', 'Помилка'


class PaymentMethod(models.TextChoices):
    CASH = 'CASH', 'Готівка'
    CARD = 'CARD', 'Картка'
    ONLINE = 'ONLINE', 'Онлайн'


class OrderDetails(models.Model):
    book = models.ForeignKey('shop.Book', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.IntegerField()
    order = models.ForeignKey('Order', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.book.title}, {self.amount}, {self.order.id}'


class Order(models.Model):
    owner = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    delivery_address = models.ForeignKey(
        'user_management.DeliveryAddress', on_delete=models.CASCADE
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    # ВИПРАВЛЕНО: додано choices щоб CharField знав допустимі значення
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CARD,
    )
    ttn = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f'{self.id} {self.owner} {self.created_at}'
