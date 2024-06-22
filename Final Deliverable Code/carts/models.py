from django.db import models
# Importing necessary models from other modules
from store.models import Product, Variation  
from accounts.models import Account
from user_interaction.models import UserInteraction

# Class to represent a cart
class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)  
    date_added = models.DateField(auto_now_add=True) 

    # Just to override the default table name
    def __str__(self):
        return self.cart_id 


# Class to represent a cart item
class CartItem(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)  
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  
    variations = models.ManyToManyField(Variation, blank=True)  
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)  
    quantity = models.IntegerField() 
    is_active = models.BooleanField(default=True)  

    # Calculate the total price for this item
    def sub_total(self):
        return self.product.price * self.quantity  

    # Just to override the default table name
    def __unicode__(self):
        return self.product  
    

            