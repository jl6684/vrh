from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from .models import UserProfile
from apps.orders.models import Order
from apps.wishlist.models import Wishlist
from apps.reviews.models import Review
from apps.vinyl.models import Genre


def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('home:index')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            login(request, user)
            return redirect('home:index')
    else:
        form = UserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """User login view"""
    if request.user.is_authenticated:
        return redirect('home:index')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                # Redirect to next page if provided
                next_page = request.GET.get('next', 'home:index')
                return redirect(next_page)
    else:
        form = AuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home:index')


@login_required
def profile_view(request):
    """User profile view"""
    # Get or create profile for the user
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Get user's recent orders (with error handling)
    try:
        recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    except:
        recent_orders = []
    
    # Get user's recent reviews (with error handling)
    try:
        recent_reviews = Review.objects.filter(user=request.user).order_by('-created_at')[:5]
    except:
        recent_reviews = []
    
    # Get wishlist count (with error handling)
    try:
        wishlist_count = Wishlist.objects.filter(user=request.user).count()
    except:
        wishlist_count = 0
    
    context = {
        'profile': profile,
        'recent_orders': recent_orders,
        'recent_reviews': recent_reviews,
        'wishlist_count': wishlist_count,
    }
    
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile_view(request):
    """Edit user profile view"""
    # Get or create profile for the user
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    all_genres = Genre.objects.all().order_by('name')
    
    if request.method == 'POST':
        # Update User model fields
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        
        # Update UserProfile fields
        profile.phone = request.POST.get('phone', '')
        
        # Handle birth_date
        birth_date = request.POST.get('birth_date')
        if birth_date:
            try:
                from datetime import datetime
                profile.birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
            except ValueError:
                profile.birth_date = None
        else:
            profile.birth_date = None
            
        profile.address_line_1 = request.POST.get('address_line_1', '')
        profile.address_line_2 = request.POST.get('address_line_2', '')
        profile.city = request.POST.get('city', '')
        profile.state = request.POST.get('state', '')
        profile.postal_code = request.POST.get('postal_code', '')
        profile.country = request.POST.get('country', 'Hong Kong')
        profile.newsletter_subscription = request.POST.get('newsletter_subscription') == 'on'
        profile.email_notifications = request.POST.get('email_notifications') == 'on'
        
        # Handle favorite genres
        selected_genres = request.POST.getlist('favorite_genres')
        profile.favorite_genres.clear()  # Clear existing selections
        for genre_id in selected_genres:
            try:
                genre = Genre.objects.get(id=genre_id)
                profile.favorite_genres.add(genre)
            except Genre.DoesNotExist:
                pass
        
        # Handle avatar upload
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        
        profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('accounts:profile')
    
    return render(request, 'accounts/edit_profile.html', {
        'profile': profile,
        'all_genres': all_genres
    })


@login_required
def order_history_view(request):
    """User order history view"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    # Use simple orders list instead of pagination for consistency
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail_view(request, order_id):
    """Individual order detail view"""
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    return render(request, 'accounts/order_detail.html', {'order': order})
