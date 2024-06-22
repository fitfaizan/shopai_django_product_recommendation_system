""" This code aims to count the number of items in a cart for a user, 
which is useful for displaying cart count information on a website. """

from .models import Cart, CartItem
from .views import _cart_id

def counter(request):
    cart_count = 0

    # Check if the path contains 'admin' and return an empty dictionary if it's an admin page
    if 'admin' in request.path:
        return {}  
    else:
        try:
            cart = Cart.objects.filter(cart_id=_cart_id(request))

            # Check if the user is authenticated
            if request.user.is_authenticated:
                cart_items = CartItem.objects.filter(user=request.user)
            else:
                # If user is not authenticated, get the cart items using the cart_id present in the session
                cart_items = CartItem.objects.filter(cart=cart[:1])

            # Calculate total cart count
            for cart_item in cart_items:
                cart_count += cart_item.quantity
        except Cart.DoesNotExist:
            # If the cart does not exist, set the cart_count to 0
            cart_count = 0

    return dict(cart_count=cart_count)
