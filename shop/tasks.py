from celery import shared_task
from django.core.cache import cache
from django.db.models import Avg, Count

from .models import Book, Category


@shared_task
def generate_catalog_report():
    report = {
        'books_count': Book.objects.count(),
        'available_books_count': Book.objects.filter(available=True, amount__gt=0).count(),
        'categories_count': Category.objects.count(),
        'average_price': str(Book.objects.aggregate(value=Avg('price'))['value'] or 0),
        'books_per_category': list(
            Category.objects.annotate(books_count=Count('book')).values('name', 'books_count')
        ),
    }
    cache.set('catalog_report', report, timeout=60 * 60)
    return report
