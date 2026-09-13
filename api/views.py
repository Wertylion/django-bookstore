from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from order.cart import Cart
from order.models import Order
from shop.models import Book, Category

from .permissions import IsAdminOrReadOnly, IsOwnerOrAdminReadOnly
from .serializers import BookSerializer, CartAddSerializer, CartSerializer, CategorySerializer, OrderSerializer


class BookViewSet(viewsets.ModelViewSet):
    """REST API endpoint for listing, filtering and managing books."""

    queryset = Book.objects.select_related('publisher').prefetch_related('author', 'category').order_by('-added_at')
    serializer_class = BookSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ('available', 'category__slug', 'publisher', 'published_year')
    search_fields = ('title', 'author__name', 'publisher__name')
    ordering_fields = ('title', 'price', 'added_at', 'published_year')


class CategoryViewSet(viewsets.ModelViewSet):
    """REST API endpoint for book categories."""

    queryset = Category.objects.order_by('name')
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ('slug',)
    search_fields = ('name',)
    ordering_fields = ('name',)


class OrderViewSet(viewsets.ModelViewSet):
    """REST API endpoint for orders owned by the authenticated user."""

    serializer_class = OrderSerializer
    queryset = Order.objects.none()
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrAdminReadOnly)
    filterset_fields = ('status', 'payment_status', 'payment_method')
    ordering_fields = ('created_at', 'total_price')

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
        queryset = Order.objects.select_related('owner', 'delivery_address').prefetch_related('items__book')
        if self.request.user.is_staff:
            return queryset.order_by('-created_at')
        return queryset.filter(owner=self.request.user).order_by('-created_at')

    def perform_update(self, serializer):
        serializer.save(owner=self.request.user)


class CartViewSet(viewsets.GenericViewSet):
    """Session cart API with add, remove and clear actions."""

    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CartSerializer
    queryset = Book.objects.none()

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(Cart(request))
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add(self, request):
        serializer = CartAddSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        Cart(request).add(
            book=serializer.validated_data['book_id'],
            quantity=serializer.validated_data['quantity'],
            override_quantity=serializer.validated_data['override'],
        )
        return Response(self.get_serializer(Cart(request)).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def remove(self, request):
        serializer = CartAddSerializer(data={**request.data, 'quantity': request.data.get('quantity', 1)})
        serializer.is_valid(raise_exception=True)
        Cart(request).remove(serializer.validated_data['book_id'])
        return Response(self.get_serializer(Cart(request)).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def clear(self, request):
        Cart(request).clear()
        return Response(self.get_serializer(Cart(request)).data, status=status.HTTP_200_OK)
