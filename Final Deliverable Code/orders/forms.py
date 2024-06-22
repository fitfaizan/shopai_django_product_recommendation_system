from django import forms
from .models import Order

# Form class for creating and updating Order instances
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
    
        # Fields from the Order model to include in the form
        fields = [
            'first_name', 'last_name', 'phone', 'email', 'address_line_1',
            'address_line_2', 'state', 'city', 'postal_code', 'order_note'
        ]
