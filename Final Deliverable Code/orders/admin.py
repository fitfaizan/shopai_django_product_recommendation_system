from django.contrib import admin
from .models import Payment, Order, OrderProduct

# Register your models here.
# Inline representation of OrderProduct within the OrderAdmin
class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('payment', 'user', 'product', 'variation', 'quantity', 'product_price', 'ordered')   
    
    extra = 0   # Number of extra empty forms to display for adding related OrderProduct items


# Class to customize the OrderAdmin
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'status', 'full_name', 'phone', 'email', 'city', 'order_total', 'shipping_fee', 'is_ordered', 'created_at']
    list_filter = ['status', 'is_ordered']
    search_fields = ['order_number', 'first_name', 'last_name', 'phone', 'email']
    list_editable = ['status']
    
    # Number of items displayed per page in the OrderAdmin list view
    list_per_page = 20
    
    # Specifies the inline classes to include in the OrderAdmin
    inlines = [OrderProductInline]

# Registering Payment, Order, and OrderProduct models with their respective customizations in the Django admin
admin.site.register(Payment)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)
