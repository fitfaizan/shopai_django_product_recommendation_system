from django.shortcuts import render, redirect, get_object_or_404
import requests 
from django.contrib.auth.decorators import login_required

# # Email Verification
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import  urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import  force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from .forms import RegistrationForm
from .models import Account
from carts.models import Cart, CartItem
from django.contrib import auth, messages
from orders.models import Order, OrderProduct
from carts.views import _cart_id

# View function for user registration
def  register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # When using Django Form, we have to use cleaned_data to get the data from request.POST
            first_name = form.cleaned_data['first_name']
            last_name  = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            address = form.cleaned_data['address']
            password = form.cleaned_data['password']
            username = email.split('@')[0]

            user = Account.objects.create_user(first_name=first_name, last_name=last_name, email=email, username=username, address=address, password=password)
            user.phone_number = phone_number
            user.save()
            messages.success(request, 'Registrated Successfully.')
            return redirect('login')
    else:
        form = RegistrationForm()       
    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)


# View function for user login
def  login(request):
    if request.method == 'POST':
        email  = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)

        # If user exists
        if user is not None:
            try:
            # Getting the cart id from the session
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)

                    # Getting the product variations by cart id
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(list(variation))
                    
                    # Get the cart items from the user to access his product variations
                    cart_item = CartItem.objects.filter(user=user)
                    existing_variation_list = []
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        existing_variation_list.append(list(existing_variation))
                        id.append(item.id)

                    # Check if the product variation already exists in the cart
                    for prdct in product_variation:
                        if prdct in existing_variation_list:
                            index = existing_variation_list.index(prdct)
                            item_id = id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                item.user = user
                                item.save()              
            except:
            # If no cart exists for guest user, then
                pass
            auth.login(request, user)

            messages.success(request, 'Logged in Successfully.')

            url = request.META.get('HTTP_REFERER')
            # It will grab the previous url from where the user was redirected to login page
            try:
                query = requests.utils.urlparse(url).query
                # next=/cart/checkout/
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
            except:
                return redirect('home')
                        
        else:
            messages.error(request, 'Invalid login credentials.')
            return redirect('login')

    return render(request, 'accounts/login.html')


# View function for user logout
@login_required(login_url='login')
def  logout(request):
    auth.logout(request)
    messages.success(request, 'Logged out Successfully.')
    return redirect('login')


# View function for forgot password 
def  forgotpassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)

            # Reset Password Email
            current_site = get_current_site(request)
            mail_subject = 'Reset your password'
            message = render_to_string('accounts/reset_password_email.html', {
                'user': user,
                'domain': current_site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(request, 'Password reset email has been sent to your email address.')
            return redirect('login')
        else: 
            messages.error(request, 'Account with this email address does not exist. Please try again.')
            return redirect('forgotpassword')
        
    return render(request, 'accounts/forgotpassword.html')

def  password_reset_validate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect('resetPassword')
    else:
        messages.error(request, 'This link has been expired.')
        return redirect('login')
    

# View function for reset password
def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successfully.')
            return redirect('login')
        else:
            messages.error(request, 'Password do not match.')
            return redirect('resetPassword')
    else:
        return render(request, 'accounts/reset_password.html')
    

# View function for my_orders in the dashboard
@login_required(login_url='login')
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'accounts/my_orders.html', context)


# View function for order_detail in the dashboard
@login_required(login_url='login')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity
    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
    }
    return render(request, 'accounts/order_detail.html', context)

