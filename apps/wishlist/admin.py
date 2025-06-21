from django.contrib import admin
from .models import Wishlist, WishlistItem


class WishlistItemInline(admin.TabularInline):
    model = WishlistItem
    extra = 0
    readonly_fields = ('created_at',)
    raw_id_fields = ('vinyl_record',)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_total_items', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('user',)
    inlines = [WishlistItemInline]
    
    def get_total_items(self, obj):
        return obj.get_total_items()
    get_total_items.short_description = 'Total Items'


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('wishlist', 'vinyl_record', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('wishlist__user__username', 'vinyl_record__title', 'vinyl_record__artist__name')
    readonly_fields = ('created_at',)
    raw_id_fields = ('wishlist', 'vinyl_record')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('wishlist__user', 'vinyl_record', 'vinyl_record__artist')
