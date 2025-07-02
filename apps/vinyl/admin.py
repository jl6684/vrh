from django.contrib import admin
from .models import Artist, Genre, Label, VinylRecord


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    ordering = ['name']


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'founded_year', 'created_at']
    list_filter = ['country', 'founded_year']
    search_fields = ['name', 'country']
    ordering = ['name']


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ['name', 'artist_type', 'country', 'formed_year', 'created_at']
    list_filter = ['artist_type', 'country', 'formed_year']
    search_fields = ['name', 'country']
    ordering = ['name']


@admin.register(VinylRecord)
class VinylRecordAdmin(admin.ModelAdmin):
    list_display = ['title', 'artist', 'genre', 'release_year', 'price', 'stock_quantity', 'is_available', 'featured']
    list_filter = ['genre', 'label', 'condition', 'speed', 'size', 'is_available', 'featured', 'release_year']
    search_fields = ['title', 'artist__name']
    list_editable = ['price', 'stock_quantity', 'is_available', 'featured']
    readonly_fields = ['slug', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'artist', 'genre', 'label', 'release_year', 'description')
        }),
        ('Physical Properties', {
            'fields': ('condition', 'speed', 'size', 'weight')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'stock_quantity', 'is_available')
        }),
        ('Media Files', {
            'fields': ('cover_image', 'audio_sample')
        }),
        ('SEO & Marketing', {
            'fields': ('slug', 'featured')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('artist', 'genre', 'label')
