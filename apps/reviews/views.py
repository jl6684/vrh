from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from django.db import transaction
from .models import Review, ReviewHelpful
from apps.vinyl.models import VinylRecord
from apps.orders.models import OrderItem
import json


def review_list_view(request, vinyl_id):
    """Display all reviews for a vinyl record"""
    vinyl_record = get_object_or_404(VinylRecord, id=vinyl_id)
    
    # Get reviews with user and helpful votes
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
    elif sort_by == 'most_helpful':
        reviews = reviews.annotate(helpful_count=Count('helpful_votes')).order_by('-helpful_count', '-created_at')
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
        rating = request.POST.get('rating')
        title = request.POST.get('title', '').strip()
        comment = request.POST.get('comment', '').strip()
        
        # Validation
        if not rating or not title or not comment:
            messages.error(request, 'Please fill in all required fields')
            return render(request, 'reviews/write_review.html', {
                'vinyl_record': vinyl_record,
                'has_purchased': has_purchased
            })
        
        try:
            rating = int(rating)
            if not (1 <= rating <= 5):
                raise ValueError
        except ValueError:
            messages.error(request, 'Please select a valid rating')
            return render(request, 'reviews/write_review.html', {
                'vinyl_record': vinyl_record,
                'has_purchased': has_purchased
            })
        
        # Create the review
        review = Review.objects.create(
            user=request.user,
            vinyl_record=vinyl_record,
            rating=rating,
            title=title,
            comment=comment,
            is_verified_purchase=has_purchased
        )
        
        messages.success(request, 'Your review has been submitted successfully!')
        return redirect('vinyl:detail', vinyl_id=vinyl_id)
    
    context = {
        'vinyl_record': vinyl_record,
        'has_purchased': has_purchased
    }
    
    return render(request, 'reviews/write_review.html', context)


@login_required
def edit_review_view(request, review_id):
    """Edit an existing review"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        title = request.POST.get('title', '').strip()
        comment = request.POST.get('comment', '').strip()
        
        # Validation
        if not rating or not title or not comment:
            messages.error(request, 'Please fill in all required fields')
            return render(request, 'reviews/edit_review.html', {'review': review})
        
        try:
            rating = int(rating)
            if not (1 <= rating <= 5):
                raise ValueError
        except ValueError:
            messages.error(request, 'Please select a valid rating')
            return render(request, 'reviews/edit_review.html', {'review': review})
        
        # Update the review
        review.rating = rating
        review.title = title
        review.comment = comment
        review.save()
        
        messages.success(request, 'Your review has been updated successfully!')
        return redirect('vinyl:detail', vinyl_id=review.vinyl_record.id)
    
    return render(request, 'reviews/edit_review.html', {'review': review})


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
@require_http_methods(["POST"])
def mark_review_helpful(request, review_id):
    """Mark a review as helpful or unhelpful"""
    review = get_object_or_404(Review, id=review_id)
    
    # Users can't mark their own reviews as helpful
    if review.user == request.user:
        if request.content_type == 'application/json':
            return JsonResponse({
                'success': False,
                'error': 'You cannot mark your own review as helpful'
            })
        else:
            messages.error(request, 'You cannot mark your own review as helpful')
            return redirect('reviews:list', vinyl_id=review.vinyl_record.id)
    
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            is_helpful = data.get('helpful', True)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'success': False, 'error': 'Invalid data'})
    else:
        is_helpful = request.POST.get('helpful', 'true').lower() == 'true'
    
    # Check if user has already marked this review
    helpful_vote, created = ReviewHelpful.objects.get_or_create(
        user=request.user,
        review=review,
        defaults={'is_helpful': is_helpful}
    )
    
    if not created:
        # Update existing vote
        helpful_vote.is_helpful = is_helpful
        helpful_vote.save()
        action = 'updated'
    else:
        action = 'created'
    
    # Calculate new helpful counts
    helpful_count = ReviewHelpful.objects.filter(review=review, is_helpful=True).count()
    unhelpful_count = ReviewHelpful.objects.filter(review=review, is_helpful=False).count()
    
    if request.content_type == 'application/json':
        return JsonResponse({
            'success': True,
            'action': action,
            'helpful_count': helpful_count,
            'unhelpful_count': unhelpful_count,
            'user_vote': is_helpful
        })
    else:
        messages.success(request, 'Thank you for your feedback!')
        return redirect('reviews:list', vinyl_id=review.vinyl_record.id)


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
    
    # Check if current user has voted on this review
    user_vote = None
    if request.user.is_authenticated:
        try:
            helpful_vote = ReviewHelpful.objects.get(user=request.user, review=review)
            user_vote = helpful_vote.is_helpful
        except ReviewHelpful.DoesNotExist:
            pass
    
    # Get helpful counts
    helpful_count = ReviewHelpful.objects.filter(review=review, is_helpful=True).count()
    unhelpful_count = ReviewHelpful.objects.filter(review=review, is_helpful=False).count()
    
    context = {
        'review': review,
        'user_vote': user_vote,
        'helpful_count': helpful_count,
        'unhelpful_count': unhelpful_count,
    }
    
    return render(request, 'reviews/review_detail.html', context)
