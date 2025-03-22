from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'category', 'stock', 'branch', 'img']  # Ensure 'img' is included
    # Customize the price field
    price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Enter price'})
    )