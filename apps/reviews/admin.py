from django.contrib import admin
from .models import Review, ReviewHelpful


class ReviewHelpfulInline(admin.TabularInline):
    model = ReviewHelpful
    extra = 0
    readonly_fields = ('created_at',)
    raw_id_fields = ('user',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('vinyl_record', 'user', 'rating', 'title', 'is_verified_purchase', 'helpful_count', 'created_at')
    list_filter = ('rating', 'is_verified_purchase', 'created_at', 'updated_at')
    search_fields = ('vinyl_record__title', 'vinyl_record__artist__name', 'user__username', 'title', 'comment')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('user', 'vinyl_record')
    inlines = [ReviewHelpfulInline]
    
    fieldsets = (
        ('Review Information', {
            'fields': ('vinyl_record', 'user', 'rating', 'title', 'comment')
        }),
        ('Status', {
            'fields': ('is_verified_purchase', 'helpful_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'vinyl_record', 'vinyl_record__artist')


@admin.register(ReviewHelpful)
class ReviewHelpfulAdmin(admin.ModelAdmin):
    list_display = ('review', 'user', 'is_helpful', 'created_at')
    list_filter = ('is_helpful', 'created_at')
    search_fields = ('review__title', 'user__username', 'review__vinyl_record__title')
    readonly_fields = ('created_at',)
    raw_id_fields = ('user', 'review')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'review', 'review__vinyl_record')
