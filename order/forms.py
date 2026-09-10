# order/forms.py

from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Order, PaymentMethod
from user_management.models import DeliveryAddress


class NewOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['delivery_address', 'payment_method']
        labels = {
            'delivery_address': _('Delivery address'),
            'payment_method': _('Payment method'),
        }

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['delivery_address'].queryset = DeliveryAddress.objects.filter(owner=user)
        self.fields['payment_method'].choices = PaymentMethod.choices
