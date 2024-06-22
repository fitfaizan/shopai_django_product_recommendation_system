from django.contrib import admin
from .models import Product, Variation, ProductGallery
from django.utils.text import slugify
import admin_thumbnails


# Register your models here.
# Inline for ProductGallery within ProductAdmin
@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1


# Class on how to display Product model in Django admin
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'brand', 'price', 'category')
    prepopulated_fields = {'slug': ('product_name', 'brand', 'price')}
    list_filter = ('product_name', 'brand', 'category')

    # To include ProductGalleryInline within ProductAdmin
    inlines = [ProductGalleryInline]  

# Class on how to display Variation model in Django admin
class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_value',)
    list_filter = ('variation_value',)


# Registering models and their respective admins with Django admin
admin.site.register(Product, ProductAdmin)  
admin.site.register(Variation, VariationAdmin)  
admin.site.register(ProductGallery)  
