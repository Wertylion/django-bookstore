from django.contrib import admin
from django.db.models import Avg, Count

from .models import Publisher, Author, Category, Book, Rating


class RatingInline(admin.TabularInline):
    model = Rating
    extra = 1


class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'country', 'website')
    search_fields = ('name', 'city', 'country')
    list_filter = ('country',)


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')
    search_fields = ('name', 'email')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class BookAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'publisher',
        'price',
        'amount',
        'available',
        'published_year',
        'average_rating',
        'ratings_count',
    )

    list_filter = (
        'available',
        'published_year',
        'publisher',
        'category',
    )

    search_fields = (
        'title',
        'author__name',
        'publisher__name',
    )

    list_editable = (
        'price',
        'amount',
        'available',
    )

    filter_horizontal = (
        'author',
        'category',
    )

    inlines = [RatingInline]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            avg_rating=Avg('rating__rating'),
            count_rating=Count('rating')
        )

    def average_rating(self, obj):
        if obj.avg_rating:
            return round(obj.avg_rating, 2)
        return '—'

    average_rating.short_description = 'Середній рейтинг'

    def ratings_count(self, obj):
        return obj.count_rating

    ratings_count.short_description = 'Кількість оцінок'


class RatingAdmin(admin.ModelAdmin):
    list_display = (
        'book',
        'user',
        'rating',
        'feedback',
    )

    list_filter = (
        'rating',
    )

    search_fields = (
        'book__title',
        'user__name',
        'feedback',
    )


admin.site.register(Publisher, PublisherAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(Rating, RatingAdmin)