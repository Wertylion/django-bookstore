# order/views.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, TemplateView

import stripe

from shop.models import Book
from .cart import Cart
from .forms import NewOrderForm
from .models import Order, OrderItem, PaymentMethod, PaymentStatus


class CartDetailView(TemplateView):
    template_name = 'cart/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cart'] = Cart(self.request)
        return context


class CartAddView(View):
    def post(self, request, pk):
        cart = Cart(request)
        book = get_object_or_404(Book, pk=pk)
        quantity = request.POST.get('quantity', 1)
        override = request.POST.get('override') == '1'
        cart.add(book=book, quantity=quantity, override_quantity=override)
        return redirect('order:cart_detail')


class CartRemoveView(View):
    def post(self, request, pk):
        cart = Cart(request)
        book = get_object_or_404(Book, pk=pk)
        cart.remove(book)
        return redirect('order:cart_detail')


class CartClearView(View):
    def post(self, request):
        Cart(request).clear()
        return redirect('order:cart_detail')


class NewOrderView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = NewOrderForm
    template_name = 'new_order.html'
    context_object_name = 'order'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        cart = Cart(self.request)
        if len(cart) == 0:
            messages.error(self.request, 'Кошик порожній.')
            return redirect('order:cart_detail')

        with transaction.atomic():
            form.instance.owner = self.request.user
            form.instance.total_price = cart.get_total_price()
            response = super().form_valid(form)

            for item in cart:
                OrderItem.objects.create(
                    order=self.object,
                    book=item['book'],
                    price=item['price'],
                    quantity=item['quantity'],
                )

            self.send_order_email()
            cart.clear()

        return response

    def get_success_url(self):
        if self.object.payment_method == PaymentMethod.ONLINE:
            return reverse('order:create_checkout_session', args=[self.object.pk])
        return reverse('order:order_success', args=[self.object.pk])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_form'] = context['form']
        context['cart'] = Cart(self.request)
        return context

    def send_order_email(self):
        recipient = self.request.user.email
        if not recipient:
            return

        send_mail(
            subject=f'Замовлення #{self.object.pk} створено',
            message=f'Ваше замовлення на суму {self.object.total_price} створено.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=True,
        )


class CreateCheckoutSessionView(LoginRequiredMixin, View):
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk, owner=request.user)
        stripe.api_key = settings.STRIPE_SECRET_KEY

        if not settings.STRIPE_SECRET_KEY:
            messages.warning(request, 'Stripe key не налаштований. Замовлення створено без переходу до оплати.')
            return redirect('order:order_success', pk=order.pk)

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            mode='payment',
            line_items=[
                {
                    'price_data': {
                        'currency': settings.STRIPE_CURRENCY,
                        'product_data': {
                            'name': item.book.title,
                        },
                        'unit_amount': int(item.price * 100),
                    },
                    'quantity': item.quantity,
                }
                for item in order.items.select_related('book')
            ],
            success_url=request.build_absolute_uri(
                reverse('order:payment_success', args=[order.pk])
            ),
            cancel_url=request.build_absolute_uri(
                reverse('order:payment_cancel', args=[order.pk])
            ),
            metadata={
                'order_id': order.pk,
            },
        )
        return redirect(checkout_session.url)


class OrderSuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'order_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = get_object_or_404(
            Order.objects.prefetch_related('items__book'),
            pk=self.kwargs['pk'],
            owner=self.request.user,
        )
        return context


class PaymentSuccessView(OrderSuccessView):
    template_name = 'payment_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = context['order']
        if order.payment_status != PaymentStatus.COMPLETED:
            order.payment_status = PaymentStatus.COMPLETED
            order.save(update_fields=['payment_status'])
        return context


class PaymentCancelView(OrderSuccessView):
    template_name = 'payment_cancel.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = context['order']
        if order.payment_status == PaymentStatus.PENDING:
            order.payment_status = PaymentStatus.FAILED
            order.save(update_fields=['payment_status'])
        return context
