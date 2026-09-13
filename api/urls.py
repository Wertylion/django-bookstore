from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BookViewSet, CartViewSet, CategoryViewSet, OrderViewSet


router = DefaultRouter()
router.register('books', BookViewSet, basename='book')
router.register('categories', CategoryViewSet, basename='category')
router.register('orders', OrderViewSet, basename='order')
router.register('cart', CartViewSet, basename='cart')

urlpatterns = [
    path('', include(router.urls)),
]
