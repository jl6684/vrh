"""
URL configuration for vrhp1 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from debug_toolbar.toolbar import debug_toolbar_urls
# Add config libraries for django look at settings.py file
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Main apps
    path('', include('apps.home.urls')),
    path('vinyl/', include('apps.vinyl.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('accounts/', include('allauth.urls')),  # Django allauth URLs (merged with accounts)
    path('cart/', include('apps.cart.urls')),
    path('orders/', include('apps.orders.urls')),
    path('wishlist/', include('apps.wishlist.urls')),
    path('reviews/', include('apps.reviews.urls')),
    
    # Django JET URLs (must be before admin)
    path('jet/', include('jet.urls', 'jet')),
    path('jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')),
    
    # Admin
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
