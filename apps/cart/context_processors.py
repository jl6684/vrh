from .models import Cart


def cart_context(request):
    """Add cart information to all templates"""
    cart = None
    cart_items_count = 0
    cart_total = 0
    
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
        except Cart.DoesNotExist:
            pass
    else:
        # For anonymous users, use session
        session_key = request.session.session_key
        if session_key:
            try:
                cart = Cart.objects.get(session_key=session_key)
            except Cart.DoesNotExist:
                pass
    
    if cart:
        cart_items_count = cart.get_total_items()
        cart_total = cart.get_total_price()
    
    return {
        'cart': cart,
        'cart_items_count': cart_items_count,
        'cart_item_count': cart_items_count,  # Added for backwards compatibility
        'cart_total': cart_total,
    }
