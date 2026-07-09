
from django.urls import path
from .views import NewOrderView

urlpatterns = [
    path('new/', NewOrderView.as_view(), name='new_order'),
]
