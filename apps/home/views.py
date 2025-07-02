from django.shortcuts import render
from django.db.models import Count, Avg
from apps.vinyl.models import VinylRecord, Genre, Artist
from apps.accounts.models import UserProfile


def index(request):
    """Home page with personalized vinyl records based on user preferences"""
    
    # Check if user is authenticated and has favorite genres
    recommended_vinyl = None
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        user_favorite_genres = request.user.profile.favorite_genres.all()
        if user_favorite_genres.exists():
            # Get vinyl records from user's favorite genres
            recommended_vinyl = VinylRecord.objects.filter(
                is_available=True,
                stock_quantity__gt=0,
                genre__in=user_favorite_genres
            ).select_related('artist', 'genre').annotate(
                average_rating=Avg('reviews__rating'),
                review_count=Count('reviews', distinct=True)
            ).order_by('-average_rating', '-created_at')[:8]
    
    # Get latest vinyl records for hero section (fallback or additional content)
    latest_vinyl = VinylRecord.objects.filter(
        is_available=True,
        stock_quantity__gt=0
    ).select_related('artist', 'genre').annotate(
        average_rating=Avg('reviews__rating'),
        review_count=Count('reviews', distinct=True)
    ).order_by('-created_at')[:8]
    
    # Get newest vinyl records for separate section
    newest_vinyl = VinylRecord.objects.filter(is_available=True).order_by('-created_at')[:6]
    
    # Get popular genres
    popular_genres = Genre.objects.all()[:6]
    
    # Get statistics for the stats section
    stats = {
        'total_vinyl_count': VinylRecord.objects.filter(is_available=True).count(),
        'total_artists_count': Artist.objects.count(),
        'total_genres_count': Genre.objects.count(),
        'total_customers_count': UserProfile.objects.count(),
    }
    
    context = {
        'latest_vinyl': latest_vinyl,
        'recommended_vinyl': recommended_vinyl,
        'newest_vinyl': newest_vinyl,
        'popular_genres': popular_genres,
        'user_has_preferences': request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.favorite_genres.exists(),
        **stats
    }
    return render(request, 'home/index.html', context)


def about(request):
    """About page"""
    return render(request, 'home/about.html')


def contact(request):
    """Contact page"""
    return render(request, 'home/contact.html')


def recycling(request):
    """Vinyl recycling information page"""
    return render(request, 'home/recycling.html')


def terms_and_conditions(request):
    """Terms and conditions page"""
    return render(request, 'home/terms.html')
