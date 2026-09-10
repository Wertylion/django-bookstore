from django.contrib import admin
from django.db.models import Sum, F

from .models import Order, OrderDetails, OrderItem


class OrderDetailsInline(admin.TabularInline):
    model = OrderDetails
    extra = 1
    fields = ('book', 'amount', 'price', 'subtotal')
    readonly_fields = ('subtotal',)

    def subtotal(self, obj):
        if obj.pk:
            return obj.amount * obj.price
        return '—'

    subtotal.short_description = 'Сума'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('book', 'quantity', 'price', 'subtotal')
    readonly_fields = ('subtotal',)

    def subtotal(self, obj):
        if obj.pk:
            return obj.subtotal
        return '—'

    subtotal.short_description = 'Сума'


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'owner',
        'created_at',
        'status',
        'payment_status',
        'payment_method',
        'total_sum',
    )

    list_filter = (
        'status',
        'payment_status',
        'payment_method',
        'created_at',
    )

    search_fields = (
        'id',
        'owner__username',
        'owner__email',
    )

    readonly_fields = (
        'created_at',
    )

    date_hierarchy = 'created_at'
    inlines = [OrderItemInline]

    def total_sum(self, obj):
        total = obj.items.aggregate(
            total=Sum(F('quantity') * F('price'))
        )['total']

        if total:
            return total
        return 0

    total_sum.short_description = 'Сума замовлення'


class OrderDetailsAdmin(admin.ModelAdmin):
    list_display = (
        'order',
        'book',
        'amount',
        'price',
        'subtotal',
    )

    list_filter = (
        'order__status',
    )

    search_fields = (
        'order__id',
        'book__title',
    )

    def subtotal(self, obj):
        return obj.amount * obj.price

    subtotal.short_description = 'Сума'


class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        'order',
        'book',
        'quantity',
        'price',
        'subtotal',
    )
    list_filter = (
        'order__status',
    )
    search_fields = (
        'order__id',
        'book__title',
    )


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderDetails, OrderDetailsAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
