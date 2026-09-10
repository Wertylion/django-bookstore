from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class OrderStatus(models.TextChoices):

    PENDING = 'PENDING', _('Pending')
    PROCESSING = 'PROCESSING', _('Processing')
    SHIPPED = 'SHIPPED', _('Shipped')
    DELIVERED = 'DELIVERED', _('Delivered')
    CANCELED = 'CANCELED', _('Canceled')


class PaymentStatus(models.TextChoices):
    PENDING = 'PENDING', _('Pending')
    PROCESSING = 'PROCESSING', _('Processing')
    COMPLETED = 'COMPLETED', _('Completed')
    FAILED = 'FAILED', _('Failed')


class PaymentMethod(models.TextChoices):
    CASH = 'CASH', _('Cash')
    CARD = 'CARD', _('Card')
    ONLINE = 'ONLINE', _('Online')


class OrderDetails(models.Model):
    book = models.ForeignKey('shop.Book', verbose_name=_('book'), on_delete=models.CASCADE)
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=2)
    amount = models.IntegerField(_('amount'))
    order = models.ForeignKey('Order', verbose_name=_('order'), on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.book.title}, {self.amount}, {self.order.id}'


class Order(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('owner'), on_delete=models.CASCADE)
    delivery_address = models.ForeignKey(
        'user_management.DeliveryAddress', verbose_name=_('delivery address'), on_delete=models.CASCADE
    )
    total_price = models.DecimalField(_('total price'), max_digits=10, decimal_places=2)
    # ВИПРАВЛЕНО: додано choices щоб CharField знав допустимі значення
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        verbose_name=_('status'),
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        verbose_name=_('payment status'),
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.CARD,
        verbose_name=_('payment method'),
    )
    ttn = models.CharField(_('tracking number'), max_length=20, blank=True)

    class Meta:
        verbose_name = _('order')
        verbose_name_plural = _('orders')

    def __str__(self):
        return f'{self.id} {self.owner} {self.created_at}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, verbose_name=_('order'), related_name='items', on_delete=models.CASCADE)
    book = models.ForeignKey('shop.Book', verbose_name=_('book'), on_delete=models.CASCADE)
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(_('quantity'), default=1)

    class Meta:
        verbose_name = _('order item')
        verbose_name_plural = _('order items')

    @property
    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f'{self.book.title}, {self.quantity}, order #{self.order_id}'
