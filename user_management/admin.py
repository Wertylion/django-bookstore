from django.contrib import admin

from .models import DeliveryAddress, LastView


class DeliveryAddressAdmin(admin.ModelAdmin):
    list_display = (
        'owner',
        'city',
        'state',
        'branch',
        'post_code',
    )

    search_fields = (
        'owner__username',
        'city',
        'post_code',
    )

    list_filter = (
        'state',
        'city',
    )


class LastViewAdmin(admin.ModelAdmin):
    list_display = (
        'owner',
        'book',
        'book_price',
    )

    search_fields = (
        'owner__username',
        'book__title',
    )

    def book_price(self, obj):
        return obj.book.price

    book_price.short_description = 'Ціна'


admin.site.register(DeliveryAddress, DeliveryAddressAdmin)
admin.site.register(LastView, LastViewAdmin)