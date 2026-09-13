from django.db import transaction
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
from rest_framework import serializers

from order.cart import Cart
from order.models import Order, OrderItem
from shop.models import Author, Book, Category, Publisher
from user_management.models import DeliveryAddress


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ('id', 'name', 'email', 'bio')


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ('id', 'name', 'address', 'city', 'state_province', 'country', 'website')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug')


class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(many=True, read_only=True)
    category = CategorySerializer(many=True, read_only=True)
    publisher = PublisherSerializer(read_only=True)
    author_ids = serializers.PrimaryKeyRelatedField(
        queryset=Author.objects.all(),
        source='author',
        many=True,
        write_only=True,
    )
    category_ids = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        many=True,
        write_only=True,
    )
    publisher_id = serializers.PrimaryKeyRelatedField(
        queryset=Publisher.objects.all(),
        source='publisher',
        write_only=True,
    )

    class Meta:
        model = Book
        fields = (
            'id',
            'title',
            'author',
            'author_ids',
            'category',
            'category_ids',
            'price',
            'added_at',
            'published_year',
            'amount',
            'available',
            'publisher',
            'publisher_id',
            'calculated_average',
        )
        read_only_fields = ('id', 'added_at')


class OrderItemSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'book', 'price', 'quantity', 'subtotal')


class OrderSerializer(serializers.ModelSerializer):
    owner = serializers.StringRelatedField(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            'id',
            'owner',
            'delivery_address',
            'total_price',
            'status',
            'created_at',
            'payment_status',
            'payment_method',
            'ttn',
            'items',
        )
        read_only_fields = ('id', 'owner', 'total_price', 'status', 'created_at', 'payment_status', 'items')

    def validate_delivery_address(self, delivery_address):
        request = self.context['request']
        if delivery_address.owner_id != request.user.id:
            raise serializers.ValidationError('Delivery address does not belong to the current user.')
        return delivery_address

    def validate(self, attrs):
        cart = Cart(self.context['request'])
        if len(cart) == 0:
            raise serializers.ValidationError('Cart is empty.')
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        request = self.context['request']
        cart = Cart(request)
        order = Order.objects.create(
            owner=request.user,
            total_price=cart.get_total_price(),
            **validated_data,
        )
        for item in cart:
            OrderItem.objects.create(
                order=order,
                book=item['book'],
                price=item['price'],
                quantity=item['quantity'],
            )
        cart.clear()
        return order


class CartItemSerializer(serializers.Serializer):
    book = BookSerializer(read_only=True)
    quantity = serializers.IntegerField(min_value=1)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)


class CartSerializer(serializers.Serializer):
    items = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    total_quantity = serializers.SerializerMethodField()

    @extend_schema_field(CartItemSerializer(many=True))
    def get_items(self, obj):
        return CartItemSerializer(list(obj), many=True).data

    @extend_schema_field(OpenApiTypes.DECIMAL)
    def get_total_price(self, obj):
        return obj.get_total_price()

    @extend_schema_field(OpenApiTypes.INT)
    def get_total_quantity(self, obj):
        return len(obj)


class CartAddSerializer(serializers.Serializer):
    book_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)
    override = serializers.BooleanField(default=False)

    def validate_book_id(self, book_id):
        try:
            return Book.objects.get(pk=book_id)
        except Book.DoesNotExist as exc:
            raise serializers.ValidationError('Book not found.') from exc
