from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from .models import Order, OrderItem
from apps.cart.models import Cart, CartItem
from apps.cart.views import get_or_create_cart
from apps.vinyl.models import VinylRecord
import uuid


@login_required
def order_list_view(request):
    """List all orders for the current user"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail_view(request, order_id):
    """Display order details"""
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
@require_http_methods(["POST"])
def create_order(request):
    """Create a new order from cart contents"""
    from apps.orders.forms import CheckoutForm
    from apps.cart.views import get_or_create_cart
    
    cart = get_or_create_cart(request)
    cart_items = CartItem.objects.filter(cart=cart).select_related('vinyl_record')
    
    if not cart_items.exists():
        messages.error(request, 'Your cart is empty')
        return redirect('cart:view')
    
    # Validate form
    form = CheckoutForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'Please correct the errors in the form')
        return redirect('cart:checkout')
    
    # Validate stock availability
    for item in cart_items:
        if item.quantity > item.vinyl_record.stock_quantity:
            messages.error(request, f'Insufficient stock for {item.vinyl_record.title}')
            return redirect('cart:checkout')
    
    # Get form data
    cleaned_data = form.cleaned_data
    
    # Use billing address for shipping if shipping_same_as_billing is True
    if cleaned_data.get('shipping_same_as_billing', True):
        shipping_address_line_1 = cleaned_data['billing_address_line_1']
        shipping_address_line_2 = cleaned_data.get('billing_address_line_2', '')
        shipping_city = cleaned_data['billing_city']
        shipping_state = cleaned_data['billing_state']
        shipping_postal_code = cleaned_data['billing_postal_code']
        shipping_country = cleaned_data['billing_country']
    else:
        shipping_address_line_1 = cleaned_data['shipping_address_line_1']
        shipping_address_line_2 = cleaned_data.get('shipping_address_line_2', '')
        shipping_city = cleaned_data['shipping_city']
        shipping_state = cleaned_data['shipping_state']
        shipping_postal_code = cleaned_data['shipping_postal_code']
        shipping_country = cleaned_data['shipping_country']
    
    # Calculate totals
    subtotal = sum(item.get_total_price() for item in cart_items)
    shipping_cost = 50 if subtotal < 500 else 0
    total_amount = subtotal + shipping_cost
    
    try:
        with transaction.atomic():
            # Create the order
            order = Order.objects.create(
                user=request.user,
                email=cleaned_data['billing_email'],
                first_name=cleaned_data['billing_first_name'],
                last_name=cleaned_data['billing_last_name'],
                phone=cleaned_data.get('billing_phone', ''),
                total_amount=total_amount,
                shipping_cost=shipping_cost,
                address_line_1=shipping_address_line_1,
                address_line_2=shipping_address_line_2,
                city=shipping_city,
                state=shipping_state,
                postal_code=shipping_postal_code,
                country=shipping_country,
                notes=cleaned_data.get('order_notes', ''),
                status='pending'
            )
            
            # Create order items and update stock
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    vinyl_record=cart_item.vinyl_record,
                    quantity=cart_item.quantity,
                    price=cart_item.vinyl_record.price
                )
                
                # Update stock quantity
                vinyl = cart_item.vinyl_record
                vinyl.stock_quantity -= cart_item.quantity
                vinyl.save()
            
            # Clear the cart
            cart_items.delete()
            
            # Send confirmation email
            send_order_confirmation_email(order)
            
            messages.success(request, f'Order #{order.order_number} placed successfully!')
            return redirect('orders:detail', order_id=order.order_id)
            
    except Exception as e:
        messages.error(request, 'An error occurred while processing your order. Please try again.')
        return redirect('cart:checkout')


def send_order_confirmation_email(order):
    """Send order confirmation email to customer"""
    try:
        subject = f'Order Confirmation - #{order.order_number}'
        html_message = render_to_string('emails/order_confirmation.html', {'order': order})
        plain_message = render_to_string('emails/order_confirmation.txt', {'order': order})
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            html_message=html_message,
            fail_silently=True  # Don't break the order process if email fails
        )
    except Exception as e:
        # Log the error but don't break the order process
        pass


@login_required
def order_tracking_view(request, order_id):
    """Display order tracking information"""
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    return render(request, 'orders/order_tracking.html', {'order': order})


@login_required
@require_http_methods(["POST"])
def cancel_order(request, order_id):
    """Cancel an order (only if status is pending or confirmed)"""
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    
    if order.status not in ['pending', 'confirmed']:
        messages.error(request, 'This order cannot be cancelled')
        return redirect('orders:detail', order_id=order.order_id)
    
    try:
        with transaction.atomic():
            # Restore stock quantities
            for item in order.items.all():
                vinyl = item.vinyl_record
                vinyl.stock_quantity += item.quantity
                vinyl.save()
            
            # Update order status
            order.status = 'cancelled'
            order.save()
            
            messages.success(request, f'Order #{order.order_number} has been cancelled')
            
    except Exception as e:
        messages.error(request, 'An error occurred while cancelling your order')
    
    return redirect('orders:detail', order_id=order.order_id)


@login_required
def invoice_view(request, order_id):
    """Display printable invoice"""
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    return render(request, 'orders/invoice.html', {'order': order})
