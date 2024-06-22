from django.shortcuts import render, redirect
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.contrib.auth.models import AnonymousUser
import datetime
import json

from .forms import OrderForm
from carts.models import CartItem, Cart
from .models import Order, Payment, OrderProduct
from store.models import Product

from carts.views import _cart_id


# Create your views here.
# View for handling payment processing
def payments(request):
    if request.user.is_authenticated:
        # If user is authenticated, process the payment for the order
        body = json.loads(request.body)
        order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

        # Store transaction details inside Payment Model
        payment = Payment(
            user = request.user,
            payment_id = body['transID'],
            payment_method = body['payment_method'],
            amount_paid = order.order_total,
            status = body['status'],
        )
        payment.save()

        order.payment = payment
        order.is_ordered = True
        order.save()

        # Move the cart items to Order Product Table
        cart_items = CartItem.objects.filter(user=request.user)

        for item in cart_items:
            orderproduct = OrderProduct()
            orderproduct.order_id = order.id
            orderproduct.payment = payment
            orderproduct.user_id = request.user.id
            orderproduct.product_id = item.product_id
            orderproduct.quantity = item.quantity
            orderproduct.product_price = item.product.price
            orderproduct.ordered = True
            orderproduct.save()

            cart_item = CartItem.objects.get(id=item.id)
            product_variation = cart_item.variations.all()
            orderproduct = OrderProduct.objects.get(id=orderproduct.id)
            orderproduct.variation.set(product_variation)
            orderproduct.save()

        # Clear the cart
        CartItem.objects.filter(user=request.user).delete()

        # Send order number and transaction ID back to sendData method via JsonResponse
        data = {
            'order_number': order.order_number,
            'transID': payment.payment_id,
        }
        return JsonResponse(data)
    else:
        body = json.loads(request.body)
        # Create a new order without associating it with any user
        order = Order.objects.get(
            user=None,
            is_ordered=False, order_number=body['orderID']
        )
        
        # Store transaction details inside Payment Model
        payment = Payment(
            user = None,
            payment_id = body['transID'],
            payment_method = body['payment_method'],
            amount_paid = order.order_total,
            status = body['status'],
        )
        payment.save()

        order.payment = payment
        order.is_ordered = True
        order.save()

        # Move the cart items to Order Product Table
        cart_items = CartItem.objects.all()

        for item in cart_items:
            orderproduct = OrderProduct()
            orderproduct.order_id = order.id
            orderproduct.payment = payment
            # orderproduct.user_id = request.user.id
            orderproduct.product_id = item.product_id
            orderproduct.quantity = item.quantity
            orderproduct.product_price = item.product.price
            orderproduct.ordered = True
            orderproduct.save()

            cart_item = CartItem.objects.get(id=item.id)
            product_variation = cart_item.variations.all()
            orderproduct = OrderProduct.objects.get(id=orderproduct.id)
            orderproduct.variation.set(product_variation)
            orderproduct.save()

        # Clear the cart
        CartItem.objects.all().delete()

        # Send order number and transaction ID back to sendData method via JsonResponse
        data = {
            'order_number': order.order_number,
            'transID': payment.payment_id,
        }
        return JsonResponse(data)
    

# View for handling order placement
def place_order(request, total=0, quantity=0):
    if request.user.is_authenticated:
        current_user = request.user
        cart_items = CartItem.objects.filter(user=current_user)
    else:
        current_user = None
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart)
    
    cart_count = cart_items.count()

    # If cart count is less than or equal to 0, then redirect back to shop
    if cart_count <= 0:
        return redirect('store')
        
    grand_total = 0
    shipping_fee = 0
    for cart_item in cart_items:
        total = (cart_item.product.price) * cart_item.quantity
        quantity += cart_item.quantity

    shipping_fee = (10 * total)/100
    grand_total = total + shipping_fee

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
        # Store all the billing information inside the Order model
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.postal_code = form.cleaned_data['postal_code']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.shipping_fee = shipping_fee
            data.ip = request.META.get('REMOTE_ADDR')   # This will give us user id
            data.save()

            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime('%Y%m%d')
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user = current_user, is_ordered=False, order_number=order_number)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'shipping_fee': shipping_fee,
                'grand_total': grand_total,
                
            }

            return render(request, 'orders/payments.html', context)
    else:
        return redirect('checkout')


# View for handling order completion
def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        payment = Payment.objects.get(payment_id=transID)

        
        ordered_products = OrderProduct.objects.filter(order=order, payment=payment)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context)
        
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')
    