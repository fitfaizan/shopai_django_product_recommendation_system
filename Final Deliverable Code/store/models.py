from django.db import models
from django.urls import reverse
from category.models import Category
from accounts.models import Account


# Create your models here.
# Model for storing products
class Product(models.Model):
    product_name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brand = models.CharField(max_length=200)
    price = models.IntegerField()
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(max_length=500, blank=True)
    image = models.ImageField(upload_to='photos/products', blank=True, default='photos/products/no-image.png')
    is_available = models.BooleanField(default=True)


    # URL generation for a product
    def get_url(self):
        return reverse('product_detail', args=[self.category.slug, self.slug])
    
    def __str__(self):
        return self.product_name

        
# Custom manager for Variation model
class VariationManager(models.Manager):
    def sizes(self):
        return super(VariationManager, self).filter(variation_category='size', is_active=True)


# Choices for variation category
variation_choices = (
    ('size', 'size'),
)
# Model for storing product variations
class Variation(models.Model):
    # Relationship with Product model
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  
    variation_category = models.CharField(max_length=100, choices=variation_choices, blank=True)
    variation_value = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    objects = VariationManager()  # Custom manager for Variation model

    # String Representation
    def __str__(self):
        return self.variation_value

# Model for storing product images in a gallery
class ProductGallery(models.Model):
    product = models.ForeignKey(Product, default=None, on_delete=models.CASCADE)  
    image = models.ImageField(upload_to='store/products', max_length=255)

    def __str__(self):
        return self.product.product_name  # Display the product name in the admin

    class Meta:
        verbose_name = 'Product Gallery'
        verbose_name_plural = 'Product Gallery'
        