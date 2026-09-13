from django.core.cache import cache

from .models import Book


BOOK_DETAIL_CACHE_KEY = 'book_detail:{book_id}'


def get_book_detail_cache_key(book_id):
    return BOOK_DETAIL_CACHE_KEY.format(book_id=book_id)


def get_cached_book_detail(book_id):
    cache_key = get_book_detail_cache_key(book_id)
    data = cache.get(cache_key)
    if data is not None:
        return data

    book = Book.objects.select_related('publisher').prefetch_related('author', 'category').get(pk=book_id)
    data = {
        'id': book.pk,
        'title': book.title,
        'publisher': book.publisher.name,
        'authors': list(book.author.order_by('name').values_list('name', flat=True)),
        'categories': list(book.category.order_by('name').values_list('name', flat=True)),
        'price': str(book.price),
        'amount': book.amount,
        'available': book.available,
    }
    cache.set(cache_key, data, timeout=60 * 15)
    return data


async def aget_cached_book_detail(book_id):
    cache_key = get_book_detail_cache_key(book_id)
    data = await cache.aget(cache_key)
    if data is not None:
        return data

    book = await Book.objects.select_related('publisher').aget(pk=book_id)
    authors = []
    categories = []

    async for author in book.author.order_by('name').values_list('name', flat=True):
        authors.append(author)

    async for category in book.category.order_by('name').values_list('name', flat=True):
        categories.append(category)

    data = {
        'id': book.pk,
        'title': book.title,
        'publisher': book.publisher.name,
        'authors': authors,
        'categories': categories,
        'price': str(book.price),
        'amount': book.amount,
        'available': book.available,
    }
    await cache.aset(cache_key, data, timeout=60 * 15)
    return data


def invalidate_catalog_cache(book_id=None):
    if book_id:
        cache.delete(get_book_detail_cache_key(book_id))
    cache.clear()
