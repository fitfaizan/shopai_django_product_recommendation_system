from django.db import models
from accounts.models import Account
from store.models import Product

class UserInteraction(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    interaction_type = models.CharField(max_length=20) 
    interaction_date = models.DateTimeField(auto_now_add=True)

    @classmethod
    def record_interaction(cls, user=None, product=None, interaction_type=None):
        if user.is_authenticated:  
            cls.objects.create(user=user, product=product, interaction_type=interaction_type)
