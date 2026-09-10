from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, DeliveryAddress, LastView


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Додаткова інформація', {'fields': ('phone', 'address')}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Додаткова інформація', {'fields': ('email', 'phone', 'address')}),
    )

    list_display = (
        'username',
        'email',
        'phone',
        'is_staff',
        'is_active',
    )


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


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(DeliveryAddress, DeliveryAddressAdmin)
admin.site.register(LastView, LastViewAdmin)
