from django.db.models import Q, Count, Avg, Case, When, Value, IntegerField
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from .models import Book, Category


def main_page(request):
    return HttpResponse("Hello")

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

    return render(request, 'shop/book_list.html', context)


def book_search(request):
    query = request.GET.get('q', '').strip()
    books = Book.objects.none()

    if query:
        books = Book.objects.filter(
            Q(title__icontains=query) |
            Q(author__name__icontains=query) |
            Q(publisher__name__icontains=query)
        ).distinct()

    context = {
        'query': query,
        'books': books,
    }

    return render(request, 'shop/book_search.html', context)


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

    return render(request, 'shop/category_detail.html', context)


def category_stats(request):
    categories = Category.objects.annotate(
        book_count=Count('book'),
        avg_price=Avg('book__price'),
    ).order_by('-book_count')

    context = {
        'categories': categories,
    }

    return render(request, 'shop/category_stats.html', context)


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

    return render(request, 'shop/low_stock.html', context)


def author_or_title_books(request):
    search = request.GET.get('search', '')
    exclude_category = request.GET.get('exclude_category')

    books = Book.objects.filter(
        Q(author__name__icontains=search) |
        Q(title__icontains=search)
    ).distinct()

    if exclude_category:
        books = books.filter(
            ~Q(category__slug=exclude_category)
        ).distinct()

    context = {
        'books': books,
        'search': search,
    }

    return render(request, 'shop/author_books.html', context)