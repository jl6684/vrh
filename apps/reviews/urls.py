from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    # Review management
    path('write/<int:vinyl_id>/', views.write_review_view, name='write'),
    path('edit/<int:review_id>/', views.edit_review_view, name='edit'),
    path('delete/<int:review_id>/', views.delete_review, name='delete'),
    path('<int:review_id>/', views.review_detail_view, name='detail'),
    
    # Review lists
    path('vinyl/<int:vinyl_id>/', views.review_list_view, name='list'),
    path('my-reviews/', views.my_reviews_view, name='my_reviews'),
]
