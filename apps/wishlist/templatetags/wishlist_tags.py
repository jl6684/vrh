from django import template
from django.contrib.auth.models import AnonymousUser
from ..models import Wishlist, WishlistItem

register = template.Library()


@register.simple_tag(takes_context=True)
def is_in_wishlist(context, vinyl_record):
    """Check if a vinyl record is in the user's wishlist"""
    user = context['user']
    if isinstance(user, AnonymousUser) or not user.is_authenticated:
        return False
    
    try:
        wishlist = Wishlist.objects.get(user=user)
        return WishlistItem.objects.filter(wishlist=wishlist, vinyl_record=vinyl_record).exists()
    except Wishlist.DoesNotExist:
        return False


@register.inclusion_tag('wishlist/wishlist_button.html', takes_context=True)
def wishlist_button(context, vinyl_record, css_classes=''):
    """Render a wishlist button for a vinyl record"""
    user = context['user']
    in_wishlist = False
    
    if user.is_authenticated:
        try:
            wishlist = Wishlist.objects.get(user=user)
            in_wishlist = WishlistItem.objects.filter(wishlist=wishlist, vinyl_record=vinyl_record).exists()
        except Wishlist.DoesNotExist:
            in_wishlist = False
    
    return {
        'vinyl_record': vinyl_record,
        'in_wishlist': in_wishlist,
        'user': user,
        'css_classes': css_classes,
    }
