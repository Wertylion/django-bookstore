from decimal import Decimal

import pytest
from django.contrib.auth.models import Permission
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from order.models import Order, OrderItem, PaymentMethod
from shop.models import Book, Category

from .factories import (
    AuthorFactory,
    BookFactory,
    CategoryFactory,
    DeliveryAddressFactory,
    PublisherFactory,
    UserFactory,
)


pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


def authenticate(api_client, user=None):
    user = user or UserFactory()
    api_client.force_authenticate(user=user)
    return user


def grant(user, codename):
    permission = Permission.objects.get(codename=codename)
    user.user_permissions.add(permission)


def test_api_books_list_is_paginated(api_client):
    # Generated with AI, reviewed and modified.
    BookFactory(title='API Book')
    response = api_client.get('/api/books/')
    assert response.status_code == status.HTTP_200_OK
    assert 'results' in response.data


def test_api_books_page_size_is_twenty(api_client):
    # Generated with AI, reviewed and modified.
    for _ in range(21):
        BookFactory()
    response = api_client.get('/api/books/')
    assert len(response.data['results']) == 20


def test_api_books_filter_by_available(api_client):
    # Generated with AI, reviewed and modified.
    BookFactory(title='Available', available=True)
    BookFactory(title='Unavailable', available=False)
    response = api_client.get('/api/books/', {'available': 'true'})
    titles = [book['title'] for book in response.data['results']]
    assert 'Available' in titles
    assert 'Unavailable' not in titles


def test_api_books_filter_by_category_slug(api_client):
    # Generated with AI, reviewed and modified.
    category = CategoryFactory(slug='api-category')
    book = BookFactory(title='Categorized')
    book.category.set([category])
    BookFactory(title='Other')
    response = api_client.get('/api/books/', {'category__slug': 'api-category'})
    assert response.data['results'][0]['title'] == 'Categorized'


def test_api_books_search_by_title(api_client):
    # Generated with AI, reviewed and modified.
    BookFactory(title='Django REST Guide')
    response = api_client.get('/api/books/', {'search': 'REST'})
    assert response.status_code == status.HTTP_200_OK
    assert response.data['results'][0]['title'] == 'Django REST Guide'


def test_api_books_detail_has_nested_serializer_data(api_client):
    # Generated with AI, reviewed and modified.
    book = BookFactory()
    response = api_client.get(f'/api/books/{book.pk}/')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['author'][0]['name']
    assert response.data['category'][0]['slug']
    assert response.data['publisher']['name']


def test_api_book_create_requires_admin(api_client):
    # Generated with AI, reviewed and modified.
    authenticate(api_client)
    response = api_client.post('/api/books/', {})
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_api_admin_can_create_book(api_client):
    # Generated with AI, reviewed and modified.
    user = UserFactory(is_staff=True)
    authenticate(api_client, user)
    author = AuthorFactory()
    category = CategoryFactory()
    publisher = PublisherFactory()
    response = api_client.post('/api/books/', {
        'title': 'Created API Book',
        'author_ids': [author.pk],
        'category_ids': [category.pk],
        'publisher_id': publisher.pk,
        'price': '25.00',
        'published_year': 2026,
        'amount': 4,
        'available': True,
        'calculated_average': '0.00',
    }, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert Book.objects.filter(title='Created API Book').exists()


def test_api_admin_can_update_book(api_client):
    # Generated with AI, reviewed and modified.
    user = UserFactory(is_staff=True)
    authenticate(api_client, user)
    book = BookFactory(title='Old')
    response = api_client.patch(f'/api/books/{book.pk}/', {'title': 'Updated'}, format='json')
    assert response.status_code == status.HTTP_200_OK
    book.refresh_from_db()
    assert book.title == 'Updated'


def test_api_admin_can_delete_book(api_client):
    # Generated with AI, reviewed and modified.
    user = UserFactory(is_staff=True)
    authenticate(api_client, user)
    book = BookFactory()
    response = api_client.delete(f'/api/books/{book.pk}/')
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_api_categories_list(api_client):
    # Generated with AI, reviewed and modified.
    CategoryFactory(name='API Category', slug='api-category-list')
    response = api_client.get('/api/categories/')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['results']


def test_api_categories_search(api_client):
    # Generated with AI, reviewed and modified.
    CategoryFactory(name='Science Fiction', slug='science-fiction')
    response = api_client.get('/api/categories/', {'search': 'Science'})
    assert response.status_code == status.HTTP_200_OK
    assert response.data['results'][0]['name'] == 'Science Fiction'


def test_api_category_create_requires_admin(api_client):
    # Generated with AI, reviewed and modified.
    authenticate(api_client)
    response = api_client.post('/api/categories/', {'name': 'Nope', 'slug': 'nope'})
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_api_admin_can_create_category(api_client):
    # Generated with AI, reviewed and modified.
    authenticate(api_client, UserFactory(is_staff=True))
    response = api_client.post('/api/categories/', {'name': 'Created Category', 'slug': 'created-category'})
    assert response.status_code == status.HTTP_201_CREATED
    assert Category.objects.filter(slug='created-category').exists()


def test_api_cart_requires_authentication(api_client):
    # Generated with AI, reviewed and modified.
    response = api_client.get('/api/cart/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_api_cart_add_item(api_client):
    # Generated with AI, reviewed and modified.
    authenticate(api_client)
    book = BookFactory(price=Decimal('9.00'))
    response = api_client.post('/api/cart/add/', {'book_id': book.pk, 'quantity': 2}, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['total_quantity'] == 2


def test_api_cart_override_quantity(api_client):
    # Generated with AI, reviewed and modified.
    authenticate(api_client)
    book = BookFactory()
    api_client.post('/api/cart/add/', {'book_id': book.pk, 'quantity': 1}, format='json')
    response = api_client.post('/api/cart/add/', {'book_id': book.pk, 'quantity': 5, 'override': True}, format='json')
    assert response.data['total_quantity'] == 5


def test_api_cart_remove_item(api_client):
    # Generated with AI, reviewed and modified.
    authenticate(api_client)
    book = BookFactory()
    api_client.post('/api/cart/add/', {'book_id': book.pk, 'quantity': 1}, format='json')
    response = api_client.post('/api/cart/remove/', {'book_id': book.pk}, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['total_quantity'] == 0


def test_api_cart_clear(api_client):
    # Generated with AI, reviewed and modified.
    authenticate(api_client)
    api_client.post('/api/cart/add/', {'book_id': BookFactory().pk, 'quantity': 1}, format='json')
    response = api_client.post('/api/cart/clear/')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['items'] == []


def test_api_order_list_requires_authentication(api_client):
    # Generated with AI, reviewed and modified.
    response = api_client.get('/api/orders/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_api_order_create_from_cart(api_client):
    # Generated with AI, reviewed and modified.
    user = authenticate(api_client)
    address = DeliveryAddressFactory(owner=user)
    book = BookFactory(price=Decimal('30.00'))
    api_client.post('/api/cart/add/', {'book_id': book.pk, 'quantity': 2}, format='json')
    response = api_client.post('/api/orders/', {
        'delivery_address': address.pk,
        'payment_method': PaymentMethod.CASH,
    }, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['total_price'] == '60.00'
    assert OrderItem.objects.filter(order_id=response.data['id'], book=book, quantity=2).exists()


def test_api_order_create_rejects_empty_cart(api_client):
    # Generated with AI, reviewed and modified.
    user = authenticate(api_client)
    address = DeliveryAddressFactory(owner=user)
    response = api_client.post('/api/orders/', {
        'delivery_address': address.pk,
        'payment_method': PaymentMethod.CASH,
    }, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_api_order_list_shows_only_owner_orders(api_client):
    # Generated with AI, reviewed and modified.
    user = authenticate(api_client)
    own_address = DeliveryAddressFactory(owner=user)
    other_user = UserFactory()
    other_address = DeliveryAddressFactory(owner=other_user)
    own_order = Order.objects.create(owner=user, delivery_address=own_address, total_price='10.00')
    Order.objects.create(owner=other_user, delivery_address=other_address, total_price='20.00')
    response = api_client.get('/api/orders/')
    assert [order['id'] for order in response.data['results']] == [own_order.pk]


def test_api_order_detail_blocks_other_user(api_client):
    # Generated with AI, reviewed and modified.
    owner = UserFactory()
    address = DeliveryAddressFactory(owner=owner)
    order = Order.objects.create(owner=owner, delivery_address=address, total_price='10.00')
    authenticate(api_client)
    response = api_client.get(f'/api/orders/{order.pk}/')
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_api_admin_can_read_any_order(api_client):
    # Generated with AI, reviewed and modified.
    owner = UserFactory()
    address = DeliveryAddressFactory(owner=owner)
    order = Order.objects.create(owner=owner, delivery_address=address, total_price='10.00')
    authenticate(api_client, UserFactory(is_staff=True))
    response = api_client.get(f'/api/orders/{order.pk}/')
    assert response.status_code == status.HTTP_200_OK


def test_jwt_token_obtain_refresh_and_verify(api_client):
    # Generated with AI, reviewed and modified.
    UserFactory(username='jwt-user', password='StrongPass123')
    obtain = api_client.post('/api/token/', {'username': 'jwt-user', 'password': 'StrongPass123'})
    assert obtain.status_code == status.HTTP_200_OK
    refresh = api_client.post('/api/token/refresh/', {'refresh': obtain.data['refresh']})
    assert refresh.status_code == status.HTTP_200_OK
    verify = api_client.post('/api/token/verify/', {'token': obtain.data['access']})
    assert verify.status_code == status.HTTP_200_OK


def test_api_docs_endpoint_loads(api_client):
    # Generated with AI, reviewed and modified.
    response = api_client.get('/api/docs/')
    assert response.status_code == status.HTTP_200_OK


def test_api_schema_endpoint_loads(api_client):
    # Generated with AI, reviewed and modified.
    response = api_client.get('/api/schema/')
    assert response.status_code == status.HTTP_200_OK


def test_cors_headers_are_enabled(api_client):
    # Generated with AI, reviewed and modified.
    response = api_client.options('/api/books/', HTTP_ORIGIN='http://localhost:3000')
    assert response['access-control-allow-origin'] == 'http://localhost:3000'
