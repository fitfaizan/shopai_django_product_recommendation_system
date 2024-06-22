from django.shortcuts import render
from store.models import Product
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from store.utils import get_recommendations
import random

from django.shortcuts import render
from store.models import Product
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from store.utils import get_recommendations
import random

# View function for home page
def home(request):
    user_id = request.user.id if request.user.is_authenticated else None

    if user_id:
        # Get recommendations for authenticated users
        recommended_product_ids = get_recommendations(user_id)
        recommended_products = Product.objects.filter(id__in=recommended_product_ids)[:20]  # Limit recommendations to 20 products
    else:
        # For guest users, display random products
        all_products = Product.objects.all()
        recommended_products = random.sample(list(all_products), 20)

    # Pagination with 20 products per page
    paginator = Paginator(recommended_products, 20)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)

    context = {
        'recommended_products': paged_products,
        'products': paged_products,
    }
    return render(request, 'home.html', context)


# View function for  customer support page
def customer_support(request):
    return render(request, 'customer_support.html')
