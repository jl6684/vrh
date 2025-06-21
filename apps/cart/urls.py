from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    # Cart management
    path('', views.cart_view, name='view'),
    path('add/<int:vinyl_id>/', views.add_to_cart, name='add'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove'),
    path('update/<int:item_id>/', views.update_cart_item, name='update'),
    path('clear/', views.clear_cart, name='clear'),
    
    # Checkout
    path('checkout/', views.checkout_view, name='checkout'),
]
