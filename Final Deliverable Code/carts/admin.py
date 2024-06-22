from django.contrib import admin
from .models import Cart, CartItem

# class to display Cart details in admin panel
class CartAdmin(admin.ModelAdmin):
    list_display = ('cart_id', 'date_added')

# class to display CartItem details in admin panel
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'cart', 'quantity', 'is_active')


# Registering Cart and CartItem models with their respective Admin classes
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
