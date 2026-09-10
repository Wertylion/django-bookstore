
from django.urls import path
from .views import (
    CartAddView,
    CartClearView,
    CartDetailView,
    CartRemoveView,
    CreateCheckoutSessionView,
    NewOrderView,
    OrderSuccessView,
    PaymentCancelView,
    PaymentSuccessView,
)

app_name = 'order'

urlpatterns = [
    path('cart/', CartDetailView.as_view(), name='cart_detail'),
    path('cart/add/<int:pk>/', CartAddView.as_view(), name='cart_add'),
    path('cart/remove/<int:pk>/', CartRemoveView.as_view(), name='cart_remove'),
    path('cart/clear/', CartClearView.as_view(), name='cart_clear'),
    path('new/', NewOrderView.as_view(), name='new_order'),
    path('<int:pk>/success/', OrderSuccessView.as_view(), name='order_success'),
    path('<int:pk>/checkout/', CreateCheckoutSessionView.as_view(), name='create_checkout_session'),
    path('<int:pk>/payment/success/', PaymentSuccessView.as_view(), name='payment_success'),
    path('<int:pk>/payment/cancel/', PaymentCancelView.as_view(), name='payment_cancel'),
]
