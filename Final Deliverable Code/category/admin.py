from django.contrib import admin
from .models import Category


# Customizing the Category display in the admin panel
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)}
    list_display = ('category_name', 'slug')


# Register the Category model with the custom CategoryAdmin configuration
admin.site.register(Category, CategoryAdmin)
