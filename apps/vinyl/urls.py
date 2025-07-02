from django.urls import path
from . import views

app_name = 'vinyl'

urlpatterns = [
    # Vinyl listing and search
    path('', views.vinyl_list, name='list'),
    path('search/', views.vinyl_search, name='search'),
    
    # Individual vinyl detail
    path('<slug:slug>/', views.vinyl_detail, name='detail'),
    
    # Category pages
    path('categories/male/', views.male_artists, name='male'),
    path('categories/female/', views.female_artists, name='female'),
    path('categories/band/', views.band_artists, name='band'),
    path('categories/assortments/', views.assortments, name='assortments'),
    path('categories/others/', views.others, name='others'),
]
