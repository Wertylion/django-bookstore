# shop/views.py

from decimal import Decimal, InvalidOperation

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Count, Avg, Case, When, Value, IntegerField
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)

from .forms import BookForm, RatingForm
from .cache import aget_cached_book_detail, get_cached_book_detail
from .models import Book, Category, Rating


class MainPageView(TemplateView):
    """Render the public home page for the bookstore."""

    template_name = 'home.html'


class EditByOwnerMixin:
    """Allow editing a rating only when it belongs to the current user."""

    def dispatch(self, request, *args, **kwargs):
        rating = Rating.objects.filter(user=request.user, id=kwargs['pk']).first()
        if rating:
            return super().dispatch(request, *args, **kwargs)
        raise PermissionDenied


class CreateFeedbackView(LoginRequiredMixin, CreateView):
    """Create a rating for a selected book and attach it to the logged-in user."""

    model = Rating
    form_class = RatingForm
    template_name = 'feedback.html'
    success_url = reverse_lazy('shop:book_list')

    def form_valid(self, form):
        form.instance.book = get_object_or_404(Book, pk=self.kwargs['pk'])
        form.instance.user = self.request.user
        return super().form_valid(form)


class FeedbackUpdateView(LoginRequiredMixin, EditByOwnerMixin, UpdateView):
    """Update the logged-in user's existing rating."""

    model = Rating
    form_class = RatingForm
    template_name = 'feedback_update.html'
    success_url = reverse_lazy('shop:book_list')


class BookListView(ListView):
    """List books with category, price, stock filters and pagination."""

    model = Book
    template_name = 'book_list.html'
    context_object_name = 'books'
    paginate_by = 10

    @method_decorator(cache_page(60 * 5, key_prefix='book_list'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @staticmethod
    def parse_price(value):
        """Convert a query string price to Decimal or ignore invalid input."""
        if not value:
            return None
        try:
            return Decimal(value)
        except (InvalidOperation, TypeError):
            return None

    def get_queryset(self):
        books = Book.objects.prefetch_related('author', 'category').select_related('publisher')

        category_slug = self.request.GET.get('category')
        min_price = self.parse_price(self.request.GET.get('min_price'))
        max_price = self.parse_price(self.request.GET.get('max_price'))
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class BookDetailView(PermissionRequiredMixin, DetailView):
    """Show details for one book to users with view permission."""

    model = Book
    template_name = 'book_detail.html'
    context_object_name = 'book'
    permission_required = 'shop.view_book'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cached_book'] = get_cached_book_detail(self.object.pk)
        return context


class BookCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Create a book record for users with add permission."""

    model = Book
    form_class = BookForm
    template_name = 'book_form.html'
    success_url = reverse_lazy('shop:book_list')
    permission_required = 'shop.add_book'


class BookUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Update a book record for users with change permission."""

    model = Book
    form_class = BookForm
    template_name = 'book_form.html'
    success_url = reverse_lazy('shop:book_list')
    permission_required = 'shop.change_book'


class BookDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Delete a book record for users with delete permission."""

    model = Book
    template_name = 'book_confirm_delete.html'
    success_url = reverse_lazy('shop:book_list')
    permission_required = 'shop.delete_book'


class BookSearchView(ListView):
    """Search books by title, author or publisher."""

    model = Book
    template_name = 'book_search.html'
    context_object_name = 'books'

    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        if not query:
            return Book.objects.none()

        return Book.objects.filter(
            Q(title__icontains=query) |
            Q(author__name__icontains=query) |
            Q(publisher__name__icontains=query)
        ).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '').strip()
        return context


class CategoryDetailView(DetailView):
    """Show category details, related books and aggregate category statistics."""

    model = Category
    template_name = 'category_detail.html'
    context_object_name = 'category'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        books = Book.objects.filter(category=self.object).annotate(
            price_tier=Case(
                When(price__lt=100, then=Value(1)),
                When(price__lt=300, then=Value(2)),
                default=Value(3),
                output_field=IntegerField(),
            )
        ).distinct()

        context['books'] = books
        context['stats'] = books.aggregate(
            total_books=Count('id'),
            avg_price=Avg('price'),
        )
        return context


class CategoryStatsView(ListView):
    """List categories with book count and average book price."""

    model = Category
    template_name = 'category_stats.html'
    context_object_name = 'categories'

    @method_decorator(cache_page(60 * 10, key_prefix='category_stats'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Category.objects.annotate(
            book_count=Count('book'),
            avg_price=Avg('book__price'),
        ).order_by('-book_count')


class LowStockBooksView(ListView):
    """List low-stock books and expose out-of-stock books in context."""

    model = Book
    template_name = 'low_stock.html'
    context_object_name = 'low_stock'

    def get_queryset(self):
        return Book.objects.filter(
            Q(amount__lte=5) & ~Q(amount=0)
        ).order_by('amount')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['out_of_stock'] = Book.objects.filter(
            Q(amount=0) | Q(available=False)
        )
        return context


class AuthorOrTitleBooksView(ListView):
    """Search books by author or title with optional category exclusion."""

    model = Book
    template_name = 'author_books.html'
    context_object_name = 'books'

    def get_queryset(self):
        search = self.request.GET.get('search', '')
        exclude_category = self.request.GET.get('exclude_category')

        books = Book.objects.filter(
            Q(author__name__icontains=search) |
            Q(title__icontains=search)
        ).distinct()

        if exclude_category:
            books = books.filter(~Q(category__slug=exclude_category)).distinct()

        return books

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        return context


async def async_catalog_summary(request):
    """Return async JSON summary for catalog counters."""

    total_books = await Book.objects.acount()
    total_categories = await Category.objects.acount()
    available_books = await Book.objects.filter(available=True, amount__gt=0).acount()

    return JsonResponse({
        'total_books': total_books,
        'total_categories': total_categories,
        'available_books': available_books,
    })


async def async_available_books(request):
    """Return async JSON list of available books."""

    books = []
    queryset = Book.objects.filter(available=True).order_by('title').values(
        'id',
        'title',
        'price',
        'amount',
    )[:20]

    async for book in queryset:
        books.append({
            'id': book['id'],
            'title': book['title'],
            'price': str(book['price']),
            'amount': book['amount'],
        })

    return JsonResponse({'books': books})


async def async_book_detail(request, pk):
    """Return async JSON details for one book."""

    try:
        data = await aget_cached_book_detail(pk)
    except Book.DoesNotExist:
        return JsonResponse({'detail': 'Book not found.'}, status=404)
    return JsonResponse(data)
