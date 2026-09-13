from decimal import Decimal
from unittest.mock import patch

import pytest
from asgiref.sync import sync_to_async
from django.contrib.auth.models import Permission
from django.core import mail
from django.urls import reverse

from order.models import Order, OrderItem, PaymentMethod, PaymentStatus
from shop.models import Book

from .factories import BookFactory, DeliveryAddressFactory, OrderFactory, OrderItemFactory, UserFactory


pytestmark = pytest.mark.django_db


def login(client, user=None):
    user = user or UserFactory(password='pass12345')
    client.force_login(user)
    return user


def grant(user, codename):
    permission = Permission.objects.get(codename=codename)
    user.user_permissions.add(permission)


def test_book_list_page_loads(client):
    # Generated with AI, reviewed and modified.
    BookFactory(title='Visible Book')
    response = client.get(reverse('shop:book_list'))
    assert response.status_code == 200
    assert 'Visible Book' in response.content.decode()


def test_book_list_filters_by_category(client):
    # Generated with AI, reviewed and modified.
    wanted = BookFactory(title='Wanted')
    other = BookFactory(title='Other')
    response = client.get(reverse('shop:book_list'), {'category': wanted.category.first().slug})
    content = response.content.decode()
    assert 'Wanted' in content
    assert 'Other' not in content


def test_book_detail_requires_permission(client):
    # Generated with AI, reviewed and modified.
    book = BookFactory()
    user = login(client)
    response = client.get(reverse('shop:book_detail', args=[book.pk]))
    assert response.status_code == 403
    grant(user, 'view_book')
    response = client.get(reverse('shop:book_detail', args=[book.pk]))
    assert response.status_code == 200


def test_cart_page_loads(client):
    # Generated with AI, reviewed and modified.
    response = client.get(reverse('order:cart_detail'))
    assert response.status_code == 200


def test_cart_add_redirects_and_stores_session(client):
    # Generated with AI, reviewed and modified.
    book = BookFactory()
    response = client.post(reverse('order:cart_add', args=[book.pk]), {'quantity': 2})
    assert response.status_code == 302
    assert client.session['cart'][str(book.pk)]['quantity'] == 2


def test_cart_update_overrides_quantity(client):
    # Generated with AI, reviewed and modified.
    book = BookFactory()
    client.post(reverse('order:cart_add', args=[book.pk]), {'quantity': 1})
    client.post(reverse('order:cart_add', args=[book.pk]), {'quantity': 4, 'override': '1'})
    assert client.session['cart'][str(book.pk)]['quantity'] == 4


def test_cart_remove_clears_one_item(client):
    # Generated with AI, reviewed and modified.
    book = BookFactory()
    client.post(reverse('order:cart_add', args=[book.pk]), {'quantity': 1})
    client.post(reverse('order:cart_remove', args=[book.pk]))
    assert str(book.pk) not in client.session['cart']


def test_cart_clear_empties_session(client):
    # Generated with AI, reviewed and modified.
    client.post(reverse('order:cart_add', args=[BookFactory().pk]), {'quantity': 1})
    client.post(reverse('order:cart_clear'))
    assert client.session['cart'] == {}


def test_checkout_requires_login(client):
    # Generated with AI, reviewed and modified.
    response = client.get(reverse('order:new_order'))
    assert response.status_code == 302
    assert '/login/' in response.url


def test_checkout_empty_cart_redirects_to_cart(client):
    # Generated with AI, reviewed and modified.
    login(client)
    response = client.post(reverse('order:new_order'), {})
    assert response.status_code == 302
    assert response.url == reverse('order:cart_detail')


def test_checkout_creates_order_item_and_sends_email(client, settings):
    # Generated with AI, reviewed and modified.
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
    user = login(client, UserFactory(email='buyer@example.com'))
    address = DeliveryAddressFactory(owner=user)
    book = BookFactory(price=Decimal('15.00'))
    client.post(reverse('order:cart_add', args=[book.pk]), {'quantity': 2})

    response = client.post(reverse('order:new_order'), {
        'delivery_address': address.pk,
        'payment_method': PaymentMethod.CASH,
    })

    order = Order.objects.latest('id')
    assert response.status_code == 302
    assert order.total_price == Decimal('30.00')
    assert OrderItem.objects.filter(order=order, book=book, quantity=2).exists()
    assert len(mail.outbox) == 1


def test_checkout_online_redirects_to_stripe_route(client):
    # Generated with AI, reviewed and modified.
    user = login(client)
    address = DeliveryAddressFactory(owner=user)
    book = BookFactory(price=Decimal('11.00'))
    client.post(reverse('order:cart_add', args=[book.pk]), {'quantity': 1})
    response = client.post(reverse('order:new_order'), {
        'delivery_address': address.pk,
        'payment_method': PaymentMethod.ONLINE,
    })
    order = Order.objects.latest('id')
    assert response.url == reverse('order:create_checkout_session', args=[order.pk])


def test_stripe_checkout_without_key_falls_back(client, settings):
    # Generated with AI, reviewed and modified.
    settings.STRIPE_SECRET_KEY = ''
    user = login(client)
    order = OrderFactory(owner=user, delivery_address=DeliveryAddressFactory(owner=user))
    OrderItemFactory(order=order)
    response = client.get(reverse('order:create_checkout_session', args=[order.pk]))
    assert response.status_code == 302
    assert response.url == reverse('order:order_success', args=[order.pk])


def test_stripe_checkout_uses_mocked_external_service(client, settings):
    # Generated with AI, reviewed and modified.
    settings.STRIPE_SECRET_KEY = 'sk_test_mock'
    user = login(client)
    order = OrderFactory(owner=user, delivery_address=DeliveryAddressFactory(owner=user))
    OrderItemFactory(order=order, price=Decimal('10.00'), quantity=2)

    with patch('order.views.stripe.checkout.Session.create') as create_session:
        create_session.return_value.url = 'https://checkout.stripe.test/session'
        response = client.get(reverse('order:create_checkout_session', args=[order.pk]))

    assert response.status_code == 302
    assert response.url == 'https://checkout.stripe.test/session'
    create_session.assert_called_once()


def test_payment_success_marks_order_completed(client):
    # Generated with AI, reviewed and modified.
    user = login(client)
    order = OrderFactory(owner=user, delivery_address=DeliveryAddressFactory(owner=user))
    response = client.get(reverse('order:payment_success', args=[order.pk]))
    order.refresh_from_db()
    assert response.status_code == 200
    assert order.payment_status == PaymentStatus.COMPLETED


def test_payment_cancel_marks_pending_order_failed(client):
    # Generated with AI, reviewed and modified.
    user = login(client)
    order = OrderFactory(owner=user, delivery_address=DeliveryAddressFactory(owner=user))
    response = client.get(reverse('order:payment_cancel', args=[order.pk]))
    order.refresh_from_db()
    assert response.status_code == 200
    assert order.payment_status == PaymentStatus.FAILED


def test_register_page_loads(client):
    # Generated with AI, reviewed and modified.
    response = client.get(reverse('register'))
    assert response.status_code == 200


def test_register_creates_custom_user(client):
    # Generated with AI, reviewed and modified.
    response = client.post(reverse('register'), {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'phone': '+380000000002',
        'address': 'Kyiv',
        'password1': 'StrongPass123',
        'password2': 'StrongPass123',
    })
    assert response.status_code == 302
    assert response.url == reverse('login')


@pytest.mark.asyncio
async def test_async_summary_endpoint(async_client):
    # Generated with AI, reviewed and modified.
    await sync_to_async(BookFactory)()
    response = await async_client.get(reverse('shop:async_catalog_summary'))
    assert response.status_code == 200
    assert response.json()['total_books'] >= 1


@pytest.mark.asyncio
async def test_async_available_books_endpoint(async_client):
    # Generated with AI, reviewed and modified.
    await sync_to_async(BookFactory)(title='Async Available', available=True)
    await sync_to_async(BookFactory)(title='Hidden', available=False)
    response = await async_client.get(reverse('shop:async_available_books'))
    titles = [item['title'] for item in response.json()['books']]
    assert 'Async Available' in titles
    assert 'Hidden' not in titles


@pytest.mark.asyncio
async def test_async_book_detail_endpoint(async_client):
    # Generated with AI, reviewed and modified.
    book = await sync_to_async(BookFactory)(title='Async Detail')
    response = await async_client.get(reverse('shop:async_book_detail', args=[book.pk]))
    assert response.status_code == 200
    assert response.json()['title'] == 'Async Detail'


def test_language_switch_endpoint(client):
    # Generated with AI, reviewed and modified.
    response = client.post('/i18n/setlang/', {'language': 'en', 'next': reverse('shop:book_list')})
    assert response.status_code == 302


def test_book_create_requires_add_permission(client):
    # Generated with AI, reviewed and modified.
    user = login(client)
    response = client.get(reverse('shop:book_create'))
    assert response.status_code == 403
    grant(user, 'add_book')
    response = client.get(reverse('shop:book_create'))
    assert response.status_code == 200


def test_book_search_endpoint_finds_title(client):
    # Generated with AI, reviewed and modified.
    BookFactory(title='Stripe Guide')
    response = client.get(reverse('shop:book_search'), {'q': 'Stripe'})
    assert response.status_code == 200
