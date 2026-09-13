# AI Code Review

Project: Book Store

This review was generated with AI, then checked and applied manually.

## Reviewed Area 1: `BookListView`

### Original Code

```python
class BookListView(ListView):
    model = Book
    template_name = 'book_list.html'
    context_object_name = 'books'
    paginate_by = 10

    def get_queryset(self):
        books = Book.objects.prefetch_related('author', 'category').select_related('publisher')

        category_slug = self.request.GET.get('category')
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        in_stock = self.request.GET.get('in_stock')

        if category_slug:
            books = books.filter(category__slug=category_slug)
        if min_price:
            books = books.filter(price__gte=min_price)
        if max_price:
            books = books.filter(price__lte=max_price)
        if in_stock == '1':
            books = books.filter(amount__gt=0, available=True)

        return books.order_by('-added_at').distinct()
```

### AI Recommendations

- Validate price query parameters before using them in ORM filters.
- Keep `select_related` and `prefetch_related` because they reduce query count for the book list.
- Add a class docstring because this view now contains non-trivial filtering behavior.

### Applied Final Code

```python
class BookListView(ListView):
    """List books with category, price, stock filters and pagination."""

    model = Book
    template_name = 'book_list.html'
    context_object_name = 'books'
    paginate_by = 10

    @staticmethod
    def parse_price(value):
        """Convert a query string price to Decimal or ignore invalid input."""
        if not value:
            return None
        try:
            return Decimal(value)
        except (InvalidOperation, TypeError):
            return None
```

Result: invalid `min_price` or `max_price` input is ignored instead of risking a server error.

## Reviewed Area 2: `NewOrderView`

### Original Code

```python
def form_valid(self, form):
    cart = Cart(self.request)
    if len(cart) == 0:
        messages.error(self.request, 'Кошик порожній.')
        return redirect('order:cart_detail')

    with transaction.atomic():
        form.instance.owner = self.request.user
        form.instance.total_price = cart.get_total_price()
        response = super().form_valid(form)
```

### AI Recommendations

- Check for an empty cart before form validation. Otherwise a POST with missing delivery data can return form errors instead of the clearer cart redirect.
- Keep `transaction.atomic()` around order and order item creation.
- Keep email sending after the order object exists.

### Applied Final Code

```python
class NewOrderView(LoginRequiredMixin, CreateView):
    """Create an order and its items from the session cart inside one transaction."""

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST' and len(Cart(request)) == 0:
            messages.error(request, 'Кошик порожній.')
            return redirect('order:cart_detail')
        return super().dispatch(request, *args, **kwargs)
```

Result: checkout with an empty cart consistently redirects to the cart page.

## Reviewed Area 3: `CreateCheckoutSessionView`

### Original Code

```python
class CreateCheckoutSessionView(LoginRequiredMixin, View):
    def get(self, request, pk):
        order = get_object_or_404(Order, pk=pk, owner=request.user)
        stripe.api_key = settings.STRIPE_SECRET_KEY

        if not settings.STRIPE_SECRET_KEY:
            messages.warning(request, 'Stripe key не налаштований. Замовлення створено без переходу до оплати.')
            return redirect('order:order_success', pk=order.pk)
```

### AI Recommendations

- Keep owner filtering to prevent users from paying or viewing other users' orders.
- Mock `stripe.checkout.Session.create` in tests instead of calling Stripe.
- Add a docstring documenting that this is an external-service boundary.

### Applied Final Code

```python
class CreateCheckoutSessionView(LoginRequiredMixin, View):
    """Create a Stripe Checkout Session for an order owned by the user."""
```

Result: the Stripe integration stays testable and guarded by ownership checks.

## Summary

Applied recommendations:

- Safer price parsing in catalog filters.
- Earlier empty-cart validation for checkout.
- Docstrings for all views.
- Added tests for model behavior, cart behavior, checkout flow, async views, language switching and Stripe mock integration.

Rejected recommendations:

- Replacing all class-based views with function views for shorter code. This conflicts with the previous homework requirement to use specialized CBVs.
- Calling the real Stripe API in tests. External services should be mocked in automated tests.
