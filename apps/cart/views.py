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
import stripe
from django.conf import settings
from django.urls import reverse
from apps.orders.models import Order, OrderItem

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


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


@login_required
def create_checkout_session(request):
    """Create Stripe checkout session"""
    # Debug: Check if API key is set
    print(f"DEBUG: Stripe API key set: {stripe.api_key[:20] if stripe.api_key else 'NOT SET'}")
    print(f"DEBUG: Settings STRIPE_SECRET_KEY: {settings.STRIPE_SECRET_KEY[:20] if settings.STRIPE_SECRET_KEY else 'NOT SET'}")
    
    cart = get_or_create_cart(request)
    cart_items = CartItem.objects.filter(cart=cart).select_related('vinyl_record')
    
    if not cart_items.exists():
        messages.error(request, 'Your cart is empty!')
        return redirect('cart:view')
    
    try:
        # Build line items for Stripe
        line_items = []
        total_amount = 0
        
        for item in cart_items:
            line_item = {
                'price_data': {
                    'currency': settings.STRIPE_CURRENCY,
                    'product_data': {
                        'name': item.vinyl_record.title,
                        'description': f'by {item.vinyl_record.artist.name}',
                    },
                    'unit_amount': int(item.vinyl_record.price * 100),  # Convert to cents
                },
                'quantity': item.quantity,
            }
            line_items.append(line_item)
            total_amount += item.get_total_price()
        
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            customer_email=request.user.email,
            success_url=request.build_absolute_uri(reverse('cart:payment_success')) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri(reverse('cart:payment_cancel')),
            metadata={
                'user_id': request.user.id,
                'total_amount': str(total_amount),
            }
        )
        
        # Store session ID in session for later use
        request.session['stripe_session_id'] = checkout_session.id
        
        return redirect(checkout_session.url, code=303)
        
    except stripe.error.StripeError as e:
        messages.error(request, f'Payment error: {str(e)}')
        return redirect('cart:view')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('cart:view')


def payment_success(request):
    """Handle successful payment"""
    session_id = request.GET.get('session_id')
    
    if not session_id:
        messages.error(request, 'Payment session not found!')
        return redirect('cart:view')
    
    try:
        # Retrieve the session from Stripe
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.payment_status == 'paid':
            # Get cart and create order
            cart = get_or_create_cart(request)
            cart_items = CartItem.objects.filter(cart=cart).select_related('vinyl_record')
            
            # Use transaction to ensure all DB operations succeed or fail together
            from django.db import transaction
            
            with transaction.atomic():
                # Create order
                order = Order.objects.create(
                    user=request.user,
                    email=request.user.email,
                    first_name=request.user.first_name or 'Customer',
                    last_name=request.user.last_name or '',
                    address_line_1='To be updated',  # User can update this later
                    city='Hong Kong',
                    postal_code='000000',
                    total_amount=int(float(session.metadata.get('total_amount', 0))),
                    status='confirmed',
                    notes=f'Stripe Payment ID: {session.payment_intent}'
                )
                
                # Create order items and update stock
                for cart_item in cart_items:
                    OrderItem.objects.create(
                        order=order,
                        vinyl_record=cart_item.vinyl_record,
                        quantity=cart_item.quantity,
                        price=cart_item.vinyl_record.price,
                        vinyl_title=cart_item.vinyl_record.title,
                        vinyl_artist=cart_item.vinyl_record.artist.name,
                        vinyl_year=cart_item.vinyl_record.release_year
                    )
                    
                    # Update stock quantity
                    vinyl = cart_item.vinyl_record
                    vinyl.stock_quantity -= cart_item.quantity
                    vinyl.save()
                
                # Clear the cart
                cart_items.delete()
            
            messages.success(request, f'Payment successful! Order #{order.order_id} has been created.')
            return render(request, 'cart/payment_success.html', {
                'order': order,
                'session': session
            })
        else:
            messages.error(request, 'Payment was not completed successfully.')
            return redirect('cart:view')
            
    except stripe.error.StripeError as e:
        messages.error(request, f'Payment verification failed: {str(e)}')
        return redirect('cart:view')


def payment_cancel(request):
    """Handle cancelled payment"""
    messages.info(request, 'Payment was cancelled. Your cart is still available.')
    return render(request, 'cart/payment_cancel.html')


@login_required
def place_order_no_payment(request):
    """Create order without payment (pay later option)"""
    cart = get_or_create_cart(request)
    cart_items = CartItem.objects.filter(cart=cart).select_related('vinyl_record')
    
    if not cart_items.exists():
        messages.error(request, 'Your cart is empty!')
        return redirect('cart:view')
    
    try:
        # Calculate total
        total_amount = sum(item.get_total_price() for item in cart_items)
        
        # Use transaction to ensure all DB operations succeed or fail together
        from django.db import transaction
        
        with transaction.atomic():
            # Create order
            order = Order.objects.create(
                user=request.user,
                email=request.user.email,
                first_name=request.user.first_name or 'Customer',
                last_name=request.user.last_name or '',
                address_line_1='To be updated',  # User can update this later
                city='Hong Kong',
                postal_code='000000',
                total_amount=int(total_amount),
                status='pending',  # Status: pending (no payment yet)
                notes='Order placed without payment - Payment pending'
            )
            
            # Create order items and update stock
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    vinyl_record=cart_item.vinyl_record,
                    quantity=cart_item.quantity,
                    price=cart_item.vinyl_record.price,
                    vinyl_title=cart_item.vinyl_record.title,
                    vinyl_artist=cart_item.vinyl_record.artist.name,
                    vinyl_year=cart_item.vinyl_record.release_year
                )
                
                # Update stock quantity
                vinyl = cart_item.vinyl_record
                vinyl.stock_quantity -= cart_item.quantity
                vinyl.save()
            
            # Clear the cart
            cart_items.delete()
        
        messages.success(request, f'Order #{order.order_id} has been created! You can pay later.')
        return render(request, 'cart/order_success.html', {
            'order': order,
            'payment_required': True
        })
        
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('cart:view')
