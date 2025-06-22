from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Wishlist, WishlistItem
from apps.vinyl.models import VinylRecord
import json


@login_required
def wishlist_view(request):
    """Display user's wishlist"""
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist_items = WishlistItem.objects.filter(wishlist=wishlist).select_related('vinyl_record').order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        wishlist_items = wishlist_items.filter(
            Q(vinyl_record__title__icontains=search_query) |
            Q(vinyl_record__artist__name__icontains=search_query) |
            Q(vinyl_record__album__icontains=search_query)
        )
    
    # Filter by availability
    availability_filter = request.GET.get('availability', '')
    if availability_filter == 'in_stock':
        wishlist_items = wishlist_items.filter(vinyl_record__stock_quantity__gt=0)
    elif availability_filter == 'out_of_stock':
        wishlist_items = wishlist_items.filter(vinyl_record__stock_quantity=0)
    
    # Pagination
    paginator = Paginator(wishlist_items, 12)  # Show 12 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'availability_filter': availability_filter,
        'total_items': wishlist_items.count()
    }
    
    return render(request, 'wishlist/wishlist.html', context)


@login_required
@require_http_methods(["POST"])
def add_to_wishlist(request, vinyl_id):
    """Add vinyl record to wishlist"""
    vinyl_record = get_object_or_404(VinylRecord, id=vinyl_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    # Check if item already in wishlist
    wishlist_item, created = WishlistItem.objects.get_or_create(
        wishlist=wishlist,
        vinyl_record=vinyl_record
    )
    
    if request.content_type == 'application/json':
        # Handle AJAX request
        if created:
            return JsonResponse({
                'success': True,
                'message': f'{vinyl_record.title} added to wishlist',
                'action': 'added'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': f'{vinyl_record.title} is already in your wishlist',
                'action': 'already_exists'
            })
    else:
        # Handle form submission
        if created:
            messages.success(request, f'{vinyl_record.title} added to wishlist')
        else:
            messages.info(request, f'{vinyl_record.title} is already in your wishlist')
        
        return redirect('vinyl:detail', vinyl_id=vinyl_id)


@login_required
@require_http_methods(["POST"])
def remove_from_wishlist(request, vinyl_id):
    """Remove vinyl record from wishlist"""
    vinyl_record = get_object_or_404(VinylRecord, id=vinyl_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    try:
        wishlist_item = WishlistItem.objects.get(wishlist=wishlist, vinyl_record=vinyl_record)
        wishlist_item.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Content-Type', ''):
            return JsonResponse({
                'success': True,
                'message': f'{vinyl_record.title} removed from wishlist',
                'action': 'removed'
            })
        else:
            messages.success(request, f'{vinyl_record.title} removed from wishlist')
            
    except WishlistItem.DoesNotExist:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Content-Type', ''):
            return JsonResponse({
                'success': False,
                'message': 'Item not found in wishlist',
                'action': 'not_found'
            })
        else:
            messages.error(request, 'Item not found in wishlist')
    
    # Redirect based on where the request came from
    next_url = request.GET.get('next', 'wishlist:view')
    if next_url == 'vinyl_detail':
        return redirect('vinyl:detail', vinyl_id=vinyl_id)
    else:
        return redirect('wishlist:view')


@login_required
@require_http_methods(["POST"])
def toggle_wishlist(request, vinyl_id):
    """Toggle vinyl record in/out of wishlist (for AJAX)"""
    vinyl_record = get_object_or_404(VinylRecord, id=vinyl_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    try:
        wishlist_item = WishlistItem.objects.get(wishlist=wishlist, vinyl_record=vinyl_record)
        wishlist_item.delete()
        in_wishlist = False
        added = False
        message = f'{vinyl_record.title} removed from wishlist'
    except WishlistItem.DoesNotExist:
        WishlistItem.objects.create(wishlist=wishlist, vinyl_record=vinyl_record)
        in_wishlist = True
        added = True
        message = f'{vinyl_record.title} added to wishlist'
    
    if request.content_type == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': message,
            'action': 'added' if added else 'removed',
            'added': added,
            'in_wishlist': in_wishlist
        })
    else:
        messages.success(request, message)
        return redirect('vinyl:detail', vinyl_id=vinyl_id)


@login_required
@require_http_methods(["POST"])
def move_to_cart(request, vinyl_id):
    """Move item from wishlist to cart"""
    vinyl_record = get_object_or_404(VinylRecord, id=vinyl_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    # Check if item is in wishlist
    try:
        wishlist_item = WishlistItem.objects.get(wishlist=wishlist, vinyl_record=vinyl_record)
    except WishlistItem.DoesNotExist:
        messages.error(request, 'Item not found in wishlist')
        return redirect('wishlist:view')
    
    # Check stock availability
    if vinyl_record.stock_quantity <= 0:
        messages.error(request, f'{vinyl_record.title} is currently out of stock')
        return redirect('wishlist:view')
    
    # Import here to avoid circular imports
    from apps.cart.views import get_or_create_cart
    from apps.cart.models import CartItem
    
    # Add to cart
    cart = get_or_create_cart(request)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        vinyl_record=vinyl_record,
        defaults={'quantity': 1}
    )
    
    if not created:
        # Update quantity if item already exists in cart
        if cart_item.quantity + 1 > vinyl_record.stock_quantity:
            messages.error(request, f'Cannot add more items. Only {vinyl_record.stock_quantity} available in stock')
            return redirect('wishlist:view')
        cart_item.quantity += 1
        cart_item.save()
    
    # Remove from wishlist
    wishlist_item.delete()
    
    messages.success(request, f'{vinyl_record.title} moved to cart')
    return redirect('wishlist:view')


@login_required
@require_http_methods(["POST"])
def clear_wishlist(request):
    """Clear all items from wishlist"""
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    count = WishlistItem.objects.filter(wishlist=wishlist).count()
    WishlistItem.objects.filter(wishlist=wishlist).delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Content-Type', ''):
        return JsonResponse({
            'success': True,
            'message': f'{count} items removed from wishlist'
        })
    else:
        messages.success(request, f'{count} items removed from wishlist')
        return redirect('wishlist:view')


@login_required
def wishlist_status(request, vinyl_id):
    """Check if vinyl is in user's wishlist (AJAX endpoint)"""
    vinyl_record = get_object_or_404(VinylRecord, id=vinyl_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    in_wishlist = WishlistItem.objects.filter(wishlist=wishlist, vinyl_record=vinyl_record).exists()
    
    return JsonResponse({
        'in_wishlist': in_wishlist
    })


@login_required
def bulk_wishlist_status(request):
    """Check wishlist status for multiple vinyl records (AJAX endpoint)"""
    vinyl_ids = request.GET.get('vinyl_ids', '').split(',')
    vinyl_ids = [id.strip() for id in vinyl_ids if id.strip().isdigit()]
    
    if not vinyl_ids:
        return JsonResponse({'error': 'No valid vinyl IDs provided'}, status=400)
    
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    wishlist_items = WishlistItem.objects.filter(
        wishlist=wishlist, 
        vinyl_record__id__in=vinyl_ids
    ).values_list('vinyl_record__id', flat=True)
    
    status = {}
    for vinyl_id in vinyl_ids:
        status[vinyl_id] = int(vinyl_id) in wishlist_items
    
    return JsonResponse({'status': status})
