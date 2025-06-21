from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('recycling/', views.recycling, name='recycling'),
    path('terms/', views.terms_and_conditions, name='terms'),
]
