from django.shortcuts import render
from django.db.models import Count, Avg
from apps.vinyl.models import VinylRecord, Genre, Artist
from apps.accounts.models import UserProfile


def index(request):
    """Home page with featured vinyl records"""
    # Get featured vinyl records (use latest if no featured field)
    featured_vinyl = VinylRecord.objects.filter(
        is_available=True,
        stock_quantity__gt=0
    ).select_related('artist', 'genre').order_by('-created_at')[:8]
    
    # Add average rating to each vinyl record
    for vinyl in featured_vinyl:
        reviews = vinyl.reviews.all()
        if reviews:
            vinyl.average_rating = int(reviews.aggregate(Avg('rating'))['rating__avg'] or 0)
        else:
            vinyl.average_rating = 0
    
    # Get latest vinyl records
    latest_vinyl = VinylRecord.objects.filter(is_available=True).order_by('-created_at')[:6]
    
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
        'featured_vinyl': featured_vinyl,
        'latest_vinyl': latest_vinyl,
        'popular_genres': popular_genres,
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
