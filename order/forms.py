# order/forms.py

from django import forms
from .models import Order
from user_management.models import DeliveryAddress


class NewOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['delivery_address', 'payment_method']
        labels = {
            'delivery_address': 'Адреса доставки',
            'payment_method': 'Спосіб оплати',
        }

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['delivery_address'].queryset = DeliveryAddress.objects.filter(owner=user)
