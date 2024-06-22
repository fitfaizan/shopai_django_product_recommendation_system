from django.db import models
from django.urls import reverse

# class for the category model
class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(max_length=255, blank=True)
    
    # To override the default plural name of the model
    class Meta:
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    # Get the URL of the category for linking in templates
    def get_url(self):
        return reverse('products_by_category', args=[self.slug])
        
    # String representation of the category
    def __str__(self):
        return self.category_name
