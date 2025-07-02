from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from .models import VinylRecord, Artist, Genre, Label


def vinyl_list(request):
    """List all available vinyl records with filtering and pagination"""
    vinyl_records = VinylRecord.objects.filter(is_available=True).select_related('artist', 'genre', 'label')
    
    # Get filter parameters
    genre_id = request.GET.get('genre_id')
    genre_name = request.GET.get('genre')
    artist_id = request.GET.get('artist_id')
    artist_name = request.GET.get('artist')
    condition = request.GET.get('condition')
    search_query = request.GET.get('q') or request.GET.get('search')
    sort_by = request.GET.get('sort', '-created_at')
    
    # Apply filters
    if genre_id:
        vinyl_records = vinyl_records.filter(genre_id=genre_id)
    
    if genre_name:
        vinyl_records = vinyl_records.filter(genre__name__icontains=genre_name)
    
    if artist_id:
        vinyl_records = vinyl_records.filter(artist_id=artist_id)
    
    if artist_name:
        vinyl_records = vinyl_records.filter(artist__name__icontains=artist_name)
    
    if condition:
        vinyl_records = vinyl_records.filter(condition=condition)
    
    if search_query:
        vinyl_records = vinyl_records.filter(
            Q(title__icontains=search_query) |
            Q(artist__name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(genre__name__icontains=search_query)
        )
    
    # Apply sorting
    if sort_by in ['price', '-price', 'release_year', '-release_year', '-created_at', 'title']:
        vinyl_records = vinyl_records.order_by(sort_by)
    
    # Add average rating and review count to each vinyl record
    vinyl_records = vinyl_records.annotate(
        average_rating=Avg('reviews__rating'),
        review_count=Count('reviews', distinct=True)
    )
    
    # Pagination
    paginator = Paginator(vinyl_records, 12)  # 12 records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all genres and artists for filter dropdown
    genres = Genre.objects.all()
    artists = Artist.objects.all().order_by('name')
    
    context = {
        'page_obj': page_obj,
        'genres': genres,
        'artists': artists,
        'current_genre': genre_id,
        'current_genre_name': genre_name,
        'current_artist': artist_id,
        'current_artist_name': artist_name,
        'current_condition': condition,
        'search_query': search_query,
        'sort_by': sort_by,
    }
    return render(request, 'vinyl/vinyl_list.html', context)


def vinyl_detail(request, slug):
    """Detailed view of a single vinyl record"""
    vinyl = get_object_or_404(VinylRecord, slug=slug, is_available=True)
    
    # Annotate with average rating and review count
    vinyl = VinylRecord.objects.filter(id=vinyl.id).annotate(
        average_rating=Avg('reviews__rating'),
        review_count=Count('reviews', distinct=True)
    ).first()
    
    # Get related vinyl records (same artist or genre)
    related_vinyl = VinylRecord.objects.filter(
        Q(artist=vinyl.artist) | Q(genre=vinyl.genre),
        is_available=True
    ).exclude(id=vinyl.id).annotate(
        average_rating=Avg('reviews__rating'),
        review_count=Count('reviews', distinct=True)
    )[:4]
    
    # Get reviews for this vinyl
    reviews = vinyl.reviews.select_related('user').order_by('-created_at')[:10]
    
    context = {
        'vinyl': vinyl,
        'related_vinyl': related_vinyl,
        'reviews': reviews,
    }
    return render(request, 'vinyl/vinyl_detail.html', context)


def vinyl_search(request):
    """Advanced search for vinyl records"""
    query = request.GET.get('q', '')
    genre_id = request.GET.get('genre')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    year_from = request.GET.get('year_from')
    year_to = request.GET.get('year_to')
    
    vinyl_records = VinylRecord.objects.filter(is_available=True).select_related('artist', 'genre', 'label')
    
    # Apply search filters
    if query:
        vinyl_records = vinyl_records.filter(
            Q(title__icontains=query) |
            Q(artist__name__icontains=query) |
            Q(description__icontains=query) |
            Q(label__name__icontains=query)
        )
    
    if genre_id:
        vinyl_records = vinyl_records.filter(genre_id=genre_id)
    
    if min_price:
        vinyl_records = vinyl_records.filter(price__gte=min_price)
    
    if max_price:
        vinyl_records = vinyl_records.filter(price__lte=max_price)
    
    if year_from:
        vinyl_records = vinyl_records.filter(release_year__gte=year_from)
    
    if year_to:
        vinyl_records = vinyl_records.filter(release_year__lte=year_to)
    
    # Add rating annotations
    vinyl_records = vinyl_records.annotate(
        average_rating=Avg('reviews__rating'),
        review_count=Count('reviews', distinct=True)
    )
    
    # Pagination
    paginator = Paginator(vinyl_records, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    genres = Genre.objects.all()
    
    context = {
        'page_obj': page_obj,
        'genres': genres,
        'search_form_data': request.GET,
    }
    return render(request, 'vinyl/vinyl_search.html', context)


# Category views (matching your existing templates)
def male_artists(request):
    """Show vinyl records by male artists"""
    vinyl_records = VinylRecord.objects.filter(
        is_available=True,
        artist__artist_type='male'
    ).select_related('artist', 'genre', 'label').annotate(
        average_rating=Avg('reviews__rating'),
        review_count=Count('reviews', distinct=True)
    )
    
    paginator = Paginator(vinyl_records, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'category_title': 'Male Artists',
    }
    return render(request, 'vinyl/category_list.html', context)


def female_artists(request):
    """Show vinyl records by female artists"""
    vinyl_records = VinylRecord.objects.filter(
        is_available=True,
        artist__artist_type='female'
    ).select_related('artist', 'genre', 'label').annotate(
        average_rating=Avg('reviews__rating'),
        review_count=Count('reviews', distinct=True)
    )
    
    paginator = Paginator(vinyl_records, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'category_title': 'Female Artists',
    }
    return render(request, 'vinyl/category_list.html', context)


def band_artists(request):
    """Show vinyl records by bands"""
    vinyl_records = VinylRecord.objects.filter(
        is_available=True,
        artist__artist_type='band'
    ).select_related('artist', 'genre', 'label').annotate(
        average_rating=Avg('reviews__rating'),
        review_count=Count('reviews', distinct=True)
    )
    
    paginator = Paginator(vinyl_records, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'category_title': 'Bands',
    }
    return render(request, 'vinyl/category_list.html', context)


def assortments(request):
    """Show assorted vinyl records"""
    vinyl_records = VinylRecord.objects.filter(
        is_available=True,
        artist__artist_type='assortment'
    ).select_related('artist', 'genre', 'label').annotate(
        average_rating=Avg('reviews__rating'),
        review_count=Count('reviews', distinct=True)
    )
    
    paginator = Paginator(vinyl_records, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'category_title': 'Assortments',
    }
    return render(request, 'vinyl/category_list.html', context)


def others(request):
    """Show other vinyl records"""
    vinyl_records = VinylRecord.objects.filter(
        is_available=True,
        artist__artist_type='other'
    ).select_related('artist', 'genre', 'label').annotate(
        average_rating=Avg('reviews__rating'),
        review_count=Count('reviews', distinct=True)
    )
    
    paginator = Paginator(vinyl_records, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'category_title': 'Others',
    }
    return render(request, 'vinyl/category_list.html', context)
