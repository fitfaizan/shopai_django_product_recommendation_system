from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator  # Models for Pagination

from django.http import HttpResponseRedirect
from django.urls import reverse
from urllib.parse import urlencode

from django.contrib.auth.models import AnonymousUser

# Your other imports and views...
# Import models from other apps
from .models import Product, ProductGallery, Variation
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from user_interaction.models import UserInteraction

# Create your views here.
# View for displaying store products with pagination
def store(request):
    products = Product.objects.filter(is_available=True).order_by('?')

    # Pagination with 20 products per page
    paginator = Paginator(products, 20)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    product_count = products.count()

    context = {
        'products': paged_products,
        'product_count': product_count,
    }

    return render(request, 'store/store.html', context)


# View for displaying product details
def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()

        # Get sizes for the single_product using VariationManager
        sizes = Variation.objects.sizes().filter(product=single_product)

    except Exception as e:
        raise e
    
    # Get the Product Gallery
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)

    # Record interactions for the product detail view
    UserInteraction.record_interaction(user=request.user, product=single_product, interaction_type='view_details')

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'product_gallery': product_gallery,
        'sizes': sizes,
    }

    return render(request, 'store/product_detail.html', context)


# View for searching products
def search(request):
    categories = Category.objects.all()
    searched_products = Product.objects.filter(is_available=True)
    category_slug = request.GET.get('category')
    keyword = request.GET.get('keyword')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    selected_brand = request.GET.get('brand')

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        searched_products = searched_products.filter(category=category)

    if keyword:
        searched_products = searched_products.filter(
            Q(description__icontains=keyword) | Q(product_name__icontains=keyword)
        )

    # When a user has not given anything in prices
    if not min_price:
        min_price = 0
    else:
        min_price = int(min_price)
    if not max_price:
        max_price = 9999999
    else:
        max_price = int(max_price)

    searched_products = searched_products.filter(price__range=(min_price, max_price))

    
    # If a brand is selected, filter products by brand
    if selected_brand:
        searched_products = searched_products.filter(brand=selected_brand)


    
    # Retrieve brands for the displayed products
    displayed_products = searched_products.all()  # Ensure you have filtered products here

    brands = displayed_products.values_list('brand', flat=True).distinct()

    paginator = Paginator(searched_products, 20)
    page_number = request.GET.get('page')
    paged_products = paginator.get_page(page_number)


    # Record interactions for a subset of products in the search results only when category_slug and keyword
    num_records = 5  
    for product in searched_products[:num_records]:
        if category_slug and keyword:
            UserInteraction.record_interaction(user=request.user, product=product, interaction_type='search_result_view')

    context = {
        'products': paged_products,
        'product_count': paginator.count,
        'links': categories,
        'selected_category': category_slug,
        'search_keyword': keyword,
        'min_price': min_price if min_price != 0 else '',
        'max_price': max_price  if max_price != 9999999 else '',

        'brands': brands,
        'selected_brand': selected_brand,
        'displayed_products': displayed_products,
    }
    return render(request, 'store/search_results.html', context)
