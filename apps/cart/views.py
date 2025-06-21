from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Sum, F
from .models import Cart, CartItem
from apps.vinyl.models import VinylRecord
import json


def get_or_create_cart(request):
    """Helper function to get or create cart for user/session"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(
            user=request.user,
            defaults={'session_key': request.session.session_key}
        )
    else:
        # For anonymous users, use session
        if not request.session.session_key:
            request.session.create()
        cart, created = Cart.objects.get_or_create(
            session_key=request.session.session_key,
            user=None
        )
    return cart


def cart_view(request):
    """Display cart contents"""
    cart = get_or_create_cart(request)
    cart_items = CartItem.objects.filter(cart=cart).select_related('vinyl_record')
    
    # Calculate totals
    total_items = cart_items.aggregate(total=Sum('quantity'))['total'] or 0
    total_price = sum(item.get_total_price() for item in cart_items)
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total_items': total_items,
        'total_price': total_price,
    }
    
    return render(request, 'cart/cart.html', context)


@require_http_methods(["POST"])
def add_to_cart(request, vinyl_id):
    """Add vinyl record to cart"""
    vinyl_record = get_object_or_404(VinylRecord, id=vinyl_id)
    cart = get_or_create_cart(request)
    
    # Check if this is an AJAX request
    is_ajax = (
        request.content_type == 'application/json' or 
        request.headers.get('Content-Type') == 'application/json' or
        request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    )
    
    if is_ajax:
        # Handle AJAX request
        try:
            data = json.loads(request.body)
            quantity = int(data.get('quantity', 1))
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'success': False, 'error': 'Invalid data'})
    else:
        # Handle form submission
        quantity = int(request.POST.get('quantity', 1))
    
    # Check stock availability
    if quantity > vinyl_record.stock_quantity:
        if is_ajax:
            return JsonResponse({
                'success': False, 
                'error': f'Only {vinyl_record.stock_quantity} items available in stock'
            })
        else:
            messages.error(request, f'Only {vinyl_record.stock_quantity} items available in stock')
            return redirect('vinyl:detail', vinyl_id=vinyl_id)
    
    # Add or update cart item
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        vinyl_record=vinyl_record,
        defaults={'quantity': quantity}
    )
    
    if not created:
        # Update quantity if item already exists
        new_quantity = cart_item.quantity + quantity
        if new_quantity > vinyl_record.stock_quantity:
            if is_ajax:
                return JsonResponse({
                    'success': False, 
                    'error': f'Cannot add more items. Only {vinyl_record.stock_quantity} available in stock'
                })
            else:
                messages.error(request, f'Cannot add more items. Only {vinyl_record.stock_quantity} available in stock')
                return redirect('vinyl:detail', vinyl_id=vinyl_id)
        
        cart_item.quantity = new_quantity
        cart_item.save()
    
    if is_ajax:
        # Return JSON response for AJAX
        cart_count = CartItem.objects.filter(cart=cart).aggregate(
            total=Sum('quantity')
        )['total'] or 0
        
        return JsonResponse({
            'success': True,
            'message': f'{vinyl_record.title} added to cart',
            'cart_count': cart_count,
            'item_total': cart_item.get_total_price()
        })
    else:
        messages.success(request, f'{vinyl_record.title} added to cart')
        return redirect('vinyl:detail', vinyl_id=vinyl_id)


@require_http_methods(["POST"])
def update_cart_item(request, item_id):
    """Update cart item quantity"""
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    
    # Check if this is an AJAX request
    is_ajax = (
        request.content_type == 'application/json' or 
        request.headers.get('Content-Type') == 'application/json' or
        request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    )
    
    if is_ajax:
        try:
            data = json.loads(request.body)
            quantity = int(data.get('quantity', 1))
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'success': False, 'error': 'Invalid data'})
    else:
        quantity = int(request.POST.get('quantity', 1))
    
    if quantity <= 0:
        cart_item.delete()
        message = 'Item removed from cart'
    elif quantity > cart_item.vinyl_record.stock_quantity:
        if is_ajax:
            return JsonResponse({
                'success': False, 
                'error': f'Only {cart_item.vinyl_record.stock_quantity} items available'
            })
        else:
            messages.error(request, f'Only {cart_item.vinyl_record.stock_quantity} items available')
            return redirect('cart:view')
    else:
        cart_item.quantity = quantity
        cart_item.save()
        message = 'Cart updated'
    
    if is_ajax:
        cart_count = CartItem.objects.filter(cart=cart).aggregate(
            total=Sum('quantity')
        )['total'] or 0
        
        cart_total = sum(item.get_total_price() for item in CartItem.objects.filter(cart=cart))
        
        return JsonResponse({
            'success': True,
            'message': message,
            'cart_count': cart_count,
            'cart_total': cart_total,
            'item_total': cart_item.get_total_price() if quantity > 0 else 0
        })
    else:
        messages.success(request, message)
        return redirect('cart:view')


@require_http_methods(["POST"])
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    
    # Check if this is an AJAX request
    is_ajax = (
        request.content_type == 'application/json' or 
        request.headers.get('Content-Type') == 'application/json' or
        request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    )
    
    vinyl_title = cart_item.vinyl_record.title
    cart_item.delete()
    
    if is_ajax:
        cart_count = CartItem.objects.filter(cart=cart).aggregate(
            total=Sum('quantity')
        )['total'] or 0
        
        cart_total = sum(item.get_total_price() for item in CartItem.objects.filter(cart=cart))
        
        return JsonResponse({
            'success': True,
            'message': f'{vinyl_title} removed from cart',
            'cart_count': cart_count,
            'cart_total': cart_total
        })
    else:
        messages.success(request, f'{vinyl_title} removed from cart')
        return redirect('cart:view')


@require_http_methods(["POST"])
def clear_cart(request):
    """Clear all items from cart"""
    cart = get_or_create_cart(request)
    CartItem.objects.filter(cart=cart).delete()
    
    # Check if this is an AJAX request
    is_ajax = (
        request.content_type == 'application/json' or 
        request.headers.get('Content-Type') == 'application/json' or
        request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    )
    
    if is_ajax:
        return JsonResponse({
            'success': True,
            'message': 'Cart cleared',
            'cart_count': 0,
            'cart_total': 0
        })
    else:
        messages.success(request, 'Cart cleared')
        return redirect('cart:view')


@login_required
def checkout_view(request):
    """Checkout page"""
    from apps.orders.forms import CheckoutForm
    
    cart = get_or_create_cart(request)
    cart_items = CartItem.objects.filter(cart=cart).select_related('vinyl_record')
    
    if not cart_items.exists():
        messages.warning(request, 'Your cart is empty')
        return redirect('cart:view')
    
    # Calculate totals
    subtotal = sum(item.get_total_price() for item in cart_items)
    shipping = 50 if subtotal < 500 else 0  # Free shipping over $500
    total = subtotal + shipping
    
    # Initialize form with user data if available
    initial_data = {}
    if hasattr(request.user, 'profile'):
        profile = request.user.profile
        initial_data = {
            'billing_first_name': request.user.first_name,
            'billing_last_name': request.user.last_name,
            'billing_email': request.user.email,
            'billing_phone': getattr(profile, 'phone', ''),
            'billing_address_line_1': getattr(profile, 'address', ''),
            'billing_city': getattr(profile, 'city', ''),
            'billing_state': getattr(profile, 'state', ''),
            'billing_postal_code': getattr(profile, 'postal_code', ''),
            'billing_country': getattr(profile, 'country', 'United States'),
        }
    
    form = CheckoutForm(initial=initial_data)
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping': shipping,
        'total': total,
        'form': form,
    }
    
    return render(request, 'cart/checkout.html', context)
