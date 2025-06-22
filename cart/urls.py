from django.urls import path
from . import views


app_name = 'cart'


urlpatterns = [
    path('', views.index, name='index'),
    path('add/<int:product_id>/', views.add, name='add'),
    path('clear/', views.clear, name='clear'),
    path('purchase/', views.purchase, name='purchase'),
]