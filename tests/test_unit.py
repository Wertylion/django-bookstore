from decimal import Decimal
import json

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import RequestFactory

from order.cart import Cart
from order.forms import NewOrderForm
from order.models import OrderItem, PaymentMethod, PaymentStatus
from shop.forms import BookForm, RatingForm
from user_management.forms import CustomUserCreationForm, UserFeedbackForm
from config.views import health_check

from .factories import (
    BookFactory,
    CategoryFactory,
    DeliveryAddressFactory,
    OrderFactory,
    OrderItemFactory,
    RatingFactory,
    UserFactory,
)


pytestmark = pytest.mark.django_db


def build_cart():
    request = RequestFactory().get('/')
    class TestSession(dict):
        modified = False

    request.session = TestSession()
    return Cart(request)


def test_custom_user_has_extra_profile_fields():
    # Generated with AI, reviewed and modified.
    user = UserFactory(phone='+380991112233', address='Lviv')
    assert user.phone == '+380991112233'
    assert user.address == 'Lviv'


def test_health_check_returns_ok():
    request = RequestFactory().get('/health/')
    response = health_check(request)
    assert response.status_code == 200
    assert json.loads(response.content) == {'status': 'ok'}


def test_custom_user_model_is_active_model():
    # Generated with AI, reviewed and modified.
    assert get_user_model()._meta.label == 'user_management.CustomUser'


def test_book_str_returns_title():
    # Generated with AI, reviewed and modified.
    book = BookFactory(title='Django Book')
    assert str(book) == 'Django Book'


def test_category_str_returns_name():
    # Generated with AI, reviewed and modified.
    category = CategoryFactory(name='Programming')
    assert str(category) == 'Programming'


def test_rating_str_contains_book_user_and_rating():
    # Generated with AI, reviewed and modified.
    rating = RatingFactory(rating=4)
    assert rating.book.title in str(rating)
    assert rating.user.username in str(rating)
    assert '4' in str(rating)


def test_order_item_subtotal_multiplies_price_and_quantity():
    # Generated with AI, reviewed and modified.
    item = OrderItemFactory(price=Decimal('7.50'), quantity=3)
    assert item.subtotal == Decimal('22.50')


def test_order_str_contains_owner():
    # Generated with AI, reviewed and modified.
    order = OrderFactory()
    assert order.owner.username in str(order)


def test_cart_starts_empty():
    # Generated with AI, reviewed and modified.
    assert len(build_cart()) == 0


def test_cart_add_increases_quantity():
    # Generated with AI, reviewed and modified.
    cart = build_cart()
    book = BookFactory(price=Decimal('12.00'))
    cart.add(book, quantity=2)
    assert len(cart) == 2


def test_cart_override_quantity_replaces_quantity():
    # Generated with AI, reviewed and modified.
    cart = build_cart()
    book = BookFactory(price=Decimal('12.00'))
    cart.add(book, quantity=2)
    cart.add(book, quantity=5, override_quantity=True)
    assert len(cart) == 5


def test_cart_remove_deletes_item():
    # Generated with AI, reviewed and modified.
    cart = build_cart()
    book = BookFactory()
    cart.add(book)
    cart.remove(book)
    assert len(cart) == 0


def test_cart_clear_removes_all_items():
    # Generated with AI, reviewed and modified.
    cart = build_cart()
    cart.add(BookFactory())
    cart.add(BookFactory())
    cart.clear()
    assert len(cart) == 0


def test_cart_total_price_uses_saved_prices():
    # Generated with AI, reviewed and modified.
    cart = build_cart()
    book = BookFactory(price=Decimal('9.99'))
    cart.add(book, quantity=3)
    assert cart.get_total_price() == Decimal('29.97')


def test_rating_form_accepts_valid_rating():
    # Generated with AI, reviewed and modified.
    form = RatingForm(data={'rating': 5, 'feedback': 'Good'})
    assert form.is_valid()


def test_rating_form_rejects_missing_feedback():
    # Generated with AI, reviewed and modified.
    form = RatingForm(data={'rating': 5})
    assert not form.is_valid()


def test_book_form_accepts_valid_data():
    # Generated with AI, reviewed and modified.
    book = BookFactory()
    form = BookForm(data={
        'title': 'New Book',
        'author': [book.author.first().pk],
        'category': [book.category.first().pk],
        'price': '20.00',
        'published_year': 2025,
        'amount': 3,
        'available': 'on',
        'publisher': book.publisher.pk,
        'calculated_average': '0.00',
    })
    assert form.is_valid()


def test_user_feedback_form_requires_email():
    # Generated with AI, reviewed and modified.
    form = UserFeedbackForm(data={'name': 'Dima', 'message': 'Hi'})
    assert not form.is_valid()


def test_custom_user_creation_form_creates_custom_user():
    # Generated with AI, reviewed and modified.
    form = CustomUserCreationForm(data={
        'username': 'created',
        'email': 'created@example.com',
        'phone': '+380000000001',
        'address': 'Kyiv',
        'password1': 'StrongPass123',
        'password2': 'StrongPass123',
    })
    assert form.is_valid(), form.errors


def test_order_form_filters_delivery_addresses_by_user():
    # Generated with AI, reviewed and modified.
    user = UserFactory()
    other_user = UserFactory()
    own_address = DeliveryAddressFactory(owner=user)
    DeliveryAddressFactory(owner=other_user)
    form = NewOrderForm(user=user)
    assert list(form.fields['delivery_address'].queryset) == [own_address]


def test_payment_defaults_are_pending_and_cash_factory():
    # Generated with AI, reviewed and modified.
    order = OrderFactory(payment_method=PaymentMethod.CASH)
    assert order.payment_status == PaymentStatus.PENDING
    assert order.payment_method == PaymentMethod.CASH


def test_setup_groups_command_creates_expected_groups():
    # Generated with AI, reviewed and modified.
    call_command('setup_groups')
    assert Group.objects.filter(name='customers').exists()
    assert Group.objects.filter(name='managers').exists()
    assert Group.objects.filter(name='admins').exists()
