from django.contrib import admin
from .models import Cart, CartItem, Order, OrderItem

# Register your models here.

class CartItemInline(admin.TabularInline):
    model = CartItem
    raw_id_fields = ['product']

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    inlines = [CartItemInline]
    list_display = ['user', 'quantity', 'cart']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]
    list_display = ['id', 'user', 'created_at', 'address', 'city', 'delivery_date', 'delivered', 'shipped']
    list_filter = ['created_at', 'delivered', 'shipped']
    search_fields = ['id', 'user__username']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'price', 'quantity']

