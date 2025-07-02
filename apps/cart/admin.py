from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('vinyl_record',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_key', 'get_total_items', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'session_key')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [CartItemInline]
    
    def get_total_items(self, obj):
        return obj.items.count()
    get_total_items.short_description = 'Total Items'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'vinyl_record', 'quantity', 'get_total_price', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('cart__user__username', 'vinyl_record__title', 'vinyl_record__artist__name')
    readonly_fields = ('created_at', 'updated_at', 'get_total_price')
    raw_id_fields = ('cart', 'vinyl_record')
    
    def get_total_price(self, obj):
        return obj.get_total_price()
    get_total_price.short_description = 'Total Price'
