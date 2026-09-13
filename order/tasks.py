from celery import shared_task
from django.conf import settings
from django.contrib.sessions.models import Session
from django.core.mail import send_mail
from django.utils import timezone

from .models import Order


@shared_task
def send_order_created_email(order_id):
    order = Order.objects.select_related('owner').get(pk=order_id)
    if not order.owner.email:
        return 'No recipient email.'

    send_mail(
        subject=f'Замовлення #{order.pk} створено',
        message=f'Ваше замовлення на суму {order.total_price} створено.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[order.owner.email],
        fail_silently=True,
    )
    return f'Order email sent for #{order.pk}.'


@shared_task
def clear_expired_sessions():
    deleted_count, _ = Session.objects.filter(expire_date__lt=timezone.now()).delete()
    return deleted_count
