from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    phone = models.CharField(_('phone'), max_length=20, blank=True)
    address = models.CharField(_('address'), max_length=255, blank=True)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return self.username


class DeliveryAddress(models.Model):
    post_code = models.CharField(_('post code'), max_length=10)
    city = models.CharField(_('city'), max_length=50)
    state = models.CharField(_('state'), max_length=50)
    branch = models.CharField(_('branch'), max_length=50)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('owner'), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('delivery address')
        verbose_name_plural = _('delivery addresses')


class LastView(models.Model):
    book = models.ForeignKey('shop.Book', verbose_name=_('book'), on_delete=models.CASCADE)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('owner'), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _('last view')
        verbose_name_plural = _('last views')
