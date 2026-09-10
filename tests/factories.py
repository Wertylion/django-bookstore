from decimal import Decimal

import factory
from django.contrib.auth import get_user_model

from order.models import Order, OrderItem, PaymentMethod
from shop.models import Author, Book, Category, Publisher, Rating
from user_management.models import DeliveryAddress


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.Sequence(lambda n: f'user{n}@example.com')
    phone = '+380000000000'
    address = 'Kyiv'

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        obj.set_password(extracted or 'pass12345')
        if create:
            obj.save()


class PublisherFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Publisher

    name = factory.Sequence(lambda n: f'Publisher {n}')
    address = 'Main street'
    city = 'Kyiv'
    state_province = 'Kyiv'
    country = 'Ukraine'
    website = 'https://example.com'


class AuthorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Author

    name = factory.Sequence(lambda n: f'Author {n}')
    email = factory.Sequence(lambda n: f'author{n}@example.com')
    bio = 'Bio'


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category
        django_get_or_create = ('slug',)

    name = factory.Sequence(lambda n: f'Category {n}')
    slug = factory.Sequence(lambda n: f'category-{n}')


class BookFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Book

    title = factory.Sequence(lambda n: f'Book {n}')
    price = Decimal('10.00')
    published_year = 2024
    amount = 5
    available = True
    publisher = factory.SubFactory(PublisherFactory)

    @factory.post_generation
    def author(obj, create, extracted, **kwargs):
        if not create:
            return
        obj.author.add(*(extracted or [AuthorFactory()]))

    @factory.post_generation
    def category(obj, create, extracted, **kwargs):
        if not create:
            return
        obj.category.add(*(extracted or [CategoryFactory()]))


class RatingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Rating

    book = factory.SubFactory(BookFactory)
    user = factory.SubFactory(UserFactory)
    rating = 5
    feedback = 'Great book'


class DeliveryAddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = DeliveryAddress

    owner = factory.SubFactory(UserFactory)
    post_code = '01001'
    city = 'Kyiv'
    state = 'Kyiv'
    branch = '1'


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    owner = factory.SubFactory(UserFactory)
    delivery_address = factory.SubFactory(DeliveryAddressFactory)
    total_price = Decimal('10.00')
    payment_method = PaymentMethod.CASH


class OrderItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrderItem

    order = factory.SubFactory(OrderFactory)
    book = factory.SubFactory(BookFactory)
    price = Decimal('10.00')
    quantity = 1
