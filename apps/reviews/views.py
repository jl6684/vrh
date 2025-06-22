from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from django.db import transaction
from .models import Review
from apps.vinyl.models import VinylRecord
from apps.orders.models import OrderItem
import json


def review_list_view(request, vinyl_id):
    """Display all reviews for a vinyl record"""
    vinyl_record = get_object_or_404(VinylRecord, id=vinyl_id)
    
    # Get reviews with user
    reviews = Review.objects.filter(vinyl_record=vinyl_record).select_related('user').order_by('-created_at')
    
    # Filter by rating if specified
    rating_filter = request.GET.get('rating')
    if rating_filter:
        try:
            rating_filter = int(rating_filter)
            if 1 <= rating_filter <= 5:
                reviews = reviews.filter(rating=rating_filter)
        except ValueError:
            pass
    
    # Sort options
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'oldest':
        reviews = reviews.order_by('created_at')
    elif sort_by == 'highest_rated':
        reviews = reviews.order_by('-rating', '-created_at')
    elif sort_by == 'lowest_rated':
        reviews = reviews.order_by('rating', '-created_at')
    else:  # newest (default)
        reviews = reviews.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(reviews, 10)  # Show 10 reviews per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate review statistics
    review_stats = Review.objects.filter(vinyl_record=vinyl_record).aggregate(
        avg_rating=Avg('rating'),
        total_reviews=Count('id')
    )
    
    # Rating distribution
    rating_distribution = {}
    for i in range(1, 6):
        rating_distribution[i] = Review.objects.filter(vinyl_record=vinyl_record, rating=i).count()
    
    context = {
        'vinyl_record': vinyl_record,
        'page_obj': page_obj,
        'review_stats': review_stats,
        'rating_distribution': rating_distribution,
        'rating_filter': rating_filter,
        'sort_by': sort_by,
    }
    
    return render(request, 'reviews/review_list.html', context)


@login_required
def write_review_view(request, vinyl_id):
    """Write a review for a vinyl record"""
    from .forms import ReviewForm
    
    vinyl_record = get_object_or_404(VinylRecord, id=vinyl_id)
    
    # Check if user has already reviewed this vinyl
    existing_review = Review.objects.filter(user=request.user, vinyl_record=vinyl_record).first()
    if existing_review:
        messages.info(request, 'You have already reviewed this vinyl. You can edit your existing review.')
        return redirect('reviews:edit', review_id=existing_review.id)
    
    # Check if user has purchased this vinyl (optional requirement)
    has_purchased = OrderItem.objects.filter(
        order__user=request.user,
        vinyl_record=vinyl_record,
        order__status__in=['delivered', 'completed']
    ).exists()
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.vinyl_record = vinyl_record
            review.is_verified_purchase = has_purchased
            review.save()
            
            messages.success(request, 'Your review has been submitted successfully!')
            return redirect('vinyl:detail', slug=vinyl_record.slug)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ReviewForm()
    
    context = {
        'vinyl_record': vinyl_record,
        'form': form,
        'has_purchased': has_purchased
    }
    
    return render(request, 'reviews/write_review.html', context)


@login_required
def edit_review_view(request, review_id):
    """Edit an existing review"""
    from .forms import ReviewForm
    
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your review has been updated successfully!')
            return redirect('vinyl:detail', slug=review.vinyl_record.slug)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ReviewForm(instance=review)
    
    context = {
        'review': review,
        'form': form
    }
    
    return render(request, 'reviews/edit_review.html', context)


@login_required
@require_http_methods(["POST"])
def delete_review(request, review_id):
    """Delete a review"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    vinyl_id = review.vinyl_record.id
    
    review.delete()
    
    if request.content_type == 'application/json':
        return JsonResponse({
            'success': True,
            'message': 'Review deleted successfully'
        })
    else:
        messages.success(request, 'Your review has been deleted')
        return redirect('vinyl:detail', vinyl_id=vinyl_id)


@login_required
def my_reviews_view(request):
    """Display user's own reviews"""
    reviews = Review.objects.filter(user=request.user).select_related('vinyl_record').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(reviews, 10)  # Show 10 reviews per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'reviews/my_reviews.html', {'page_obj': page_obj})


def review_detail_view(request, review_id):
    """Display individual review detail"""
    review = get_object_or_404(Review, id=review_id)
    
    # Get other reviews for this vinyl
    other_reviews = Review.objects.filter(
        vinyl_record=review.vinyl_record
    ).exclude(id=review.id).select_related('user')[:5]
    
    context = {
        'review': review,
        'other_reviews': other_reviews,
    }
    
    return render(request, 'reviews/review_detail.html', context)
