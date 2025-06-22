from django.shortcuts import render
from django.shortcuts import redirect

# Create your views here.


def index(request):
    """Render the cart index page."""
    return render(request, 'cart/index.html')

# Logic to add a product to the cart
def add(request, id):
    #get_object_or_404(Movie, id=id)
    #cart = request.session.get('cart', {})
    #cart[id] = request.POST['quantity']
    #request.session['cart'] = cart
    return redirect('cart/index.html')

def clear(request):
    # Logic to clear the cart
    #request.session['cart'] = {}
    return redirect('cart/index.html')


def purchase(request):
    # Logic to handle the purchase process
    pass