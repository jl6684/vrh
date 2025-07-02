from django.urls import path
from . import views

app_name = 'wishlist'

urlpatterns = [
    # Wishlist management
    path('', views.wishlist_view, name='view'),
    path('add/<int:vinyl_id>/', views.add_to_wishlist, name='add'),
    path('remove/<int:vinyl_id>/', views.remove_from_wishlist, name='remove'),
    path('toggle/<int:vinyl_id>/', views.toggle_wishlist, name='toggle'),
    path('move-to-cart/<int:vinyl_id>/', views.move_to_cart, name='move_to_cart'),
    path('clear/', views.clear_wishlist, name='clear'),
    
    # AJAX endpoints
    path('status/<int:vinyl_id>/', views.wishlist_status, name='status'),
    path('bulk-status/', views.bulk_wishlist_status, name='bulk_status'),
]
