# order/views.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View

from .forms import NewOrderForm
from .models import Order, OrderDetails
from shop.models import Book


class NewOrderView(LoginRequiredMixin, View):
    def get(self, request):
        order_form = NewOrderForm(user=request.user)
        return render(request, 'new_order.html', {'order_form': order_form})

    def post(self, request):
        order_form = NewOrderForm(user=request.user, data=request.POST)
        if order_form.is_valid():
            order = order_form.save(commit=False)  # ще не зберігаємо в базу
            order.owner = request.user             # додаємо власника
            order.total_price = 0                  # поки 0, порахуємо нижче
            order.save()                           # тепер зберігаємо



            return render(request, 'order_confirmation.html', {'order': order})

        return render(request, 'new_order.html', {'order_form': order_form})
