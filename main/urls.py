from django.urls import path
from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('assortments/', views.assortments, name='assortments'),
    path('band/', views.band, name='band'),
    path('contact/', views.contact, name='contact'),
    path('female/', views.female, name='female'),
    path('male/', views.male, name='male'),
    path('others/', views.others, name='others'),
    path('recycling/', views.recycling, name='recycling'),
    path('terms/', views.terms_and_conditions, name='terms'),
]
