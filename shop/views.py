# shop/views.py

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Count, Avg, Case, When, Value, IntegerField
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from .forms import RatingForm
from .models import Book, Category, Rating


def main_page(request):
    return HttpResponse("Hello")


class EditByOwnerMixin:

    def dispatch(self, request, *args, **kwargs):
        rating = Rating.objects.filter(user=request.user, id=kwargs['pk']).first()
        if rating:
            return super().dispatch(request, *args, **kwargs)
        raise PermissionDenied


class CreateFeedbackView(LoginRequiredMixin, CreateView):
    model = Rating
    form_class = RatingForm
    template_name = 'feedback.html'
    success_url = reverse_lazy('book_list')

    def form_valid(self, form):
        form.instance.book = get_object_or_404(Book, pk=self.kwargs['pk'])
        form.instance.user = self.request.user
        return super().form_valid(form)


class FeedbackUpdateView(EditByOwnerMixin, UpdateView):
    model = Rating
    form_class = RatingForm
    template_name = 'feedback_update.html'
    success_url = reverse_lazy('book_list')

    def form_valid(self, form):
        form.instance.book = get_object_or_404(Book, pk=self.kwargs['pk'])
        form.instance.user = self.request.user
        return super().form_valid(form)


def book_list(request):
    books = Book.objects.all()

    category_slug = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    in_stock = request.GET.get('in_stock')

    if category_slug:
        books = books.filter(category__slug=category_slug)
    if min_price:
        books = books.filter(price__gte=min_price)
    if max_price:
        books = books.filter(price__lte=max_price)
    if in_stock == '1':
        books = books.filter(amount__gt=0, available=True)

    books = books.order_by('-added_at').distinct()

    context = {
        'books': books,
        'categories': Category.objects.all(),
    }
    return render(request, 'book_list.html', context)


def book_search(request):
    query = request.GET.get('q', '').strip()
    books = Book.objects.none()

    if query:
        books = Book.objects.filter(
            Q(title__icontains=query) |
            Q(author__name__icontains=query) |
            Q(publisher__name__icontains=query)
        ).distinct()

    return render(request, 'book_search.html', {'query': query, 'books': books})


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)

    books = Book.objects.filter(category=category).annotate(
        price_tier=Case(
            When(price__lt=100, then=Value(1)),
            When(price__lt=300, then=Value(2)),
            default=Value(3),
            output_field=IntegerField(),
        )
    ).distinct()

    stats = books.aggregate(
        total_books=Count('id'),
        avg_price=Avg('price'),
    )

    context = {
        'category': category,
        'books': books,
        'stats': stats,
    }
    return render(request, 'category_detail.html', context)


def category_stats(request):
    categories = Category.objects.annotate(
        book_count=Count('book'),
        avg_price=Avg('book__price'),
    ).order_by('-book_count')

    return render(request, 'category_stats.html', {'categories': categories})


def low_stock_books(request):
    low_stock = Book.objects.filter(
        Q(amount__lte=5) & ~Q(amount=0)
    ).order_by('amount')

    out_of_stock = Book.objects.filter(
        Q(amount=0) | Q(available=False)
    )

    context = {
        'low_stock': low_stock,
        'out_of_stock': out_of_stock,
    }
    return render(request, 'low_stock.html', context)


def author_or_title_books(request):
    search = request.GET.get('search', '')
    exclude_category = request.GET.get('exclude_category')

    books = Book.objects.filter(
        Q(author__name__icontains=search) |
        Q(title__icontains=search)
    ).distinct()

    if exclude_category:
        books = books.filter(~Q(category__slug=exclude_category)).distinct()

    return render(request, 'author_books.html', {'books': books, 'search': search})
