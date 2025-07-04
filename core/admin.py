from django.contrib import admin
from .models import *

# Register your models here.

class CartItemInline(admin.TabularInline):
    model = CartItem
    raw_id_fields = ['product']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    inlines = [CartItemInline]
    list_display = ['user', 'address']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']


@admin.register(DeliveryAddress)
class DeliveryAddressAdmin(admin.ModelAdmin):
    list_display = ['street', 'city', 'postal_code', 'country', 'created_at']
    search_fields = ['street', 'city', 'postal_code']
    list_filter = ['country', 'created_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ['id', 'user', 'created_at', 'address', 'delivery_date', 'status']
    list_filter = ['created_at', 'status']
    search_fields = ['id', 'user__username']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('address', 'user')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'price', 'quantity']