from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ['vinyl_title', 'vinyl_artist', 'vinyl_year', 'price', 'created_at']
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'user', 'get_full_name', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'country', 'created_at', 'shipped_at', 'delivered_at']
    search_fields = ['order_id', 'user__username', 'user__email', 'first_name', 'last_name', 'email']
    readonly_fields = ['order_id', 'created_at', 'updated_at']
    list_editable = ['status']
    ordering = ['-created_at']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_id', 'user', 'status')
        }),
        ('Customer Details', {
            'fields': ('email', 'first_name', 'last_name', 'phone')
        }),
        ('Shipping Address', {
            'fields': ('address_line_1', 'address_line_2', 'city', 'state', 'postal_code', 'country')
        }),
        ('Order Details', {
            'fields': ('total_amount', 'shipping_cost', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Customer Name'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'vinyl_title', 'vinyl_artist', 'quantity', 'price', 'get_total_price']
    list_filter = ['order__status', 'created_at']
    search_fields = ['vinyl_title', 'vinyl_artist', 'order__order_id']
    readonly_fields = ['vinyl_title', 'vinyl_artist', 'vinyl_year', 'created_at']
    ordering = ['-created_at']
    
    def get_total_price(self, obj):
        return f"${obj.get_total_price()}"
    get_total_price.short_description = 'Total Price'
