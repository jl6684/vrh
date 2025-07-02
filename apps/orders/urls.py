from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Order management
    path('', views.order_list_view, name='list'),
    path('<uuid:order_id>/', views.order_detail_view, name='detail'),
    path('<uuid:order_id>/cancel/', views.cancel_order, name='cancel'),
    path('<uuid:order_id>/tracking/', views.order_tracking_view, name='tracking'),
    path('<uuid:order_id>/invoice/', views.invoice_view, name='invoice'),
    
    # Order creation
    path('create/', views.create_order, name='create'),
]
