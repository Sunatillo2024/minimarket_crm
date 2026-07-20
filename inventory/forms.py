from django import forms
from products.models import Product

class InventoryAddForm(forms.Form):
    barcode = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Scan or enter barcode',
            'autofocus': True,
        }),
        label='Product Barcode'
    )
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Quantity',
            'min': 1,
        }),
        label='Quantity to Add'
    )
    note = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Optional note (e.g., supplier name)',
        }),
        label='Note'
    )

    def clean_barcode(self):
        barcode = self.cleaned_data.get('barcode')
        # Check if product exists
        if not Product.objects.filter(barcode=barcode).exists():
            raise forms.ValidationError(f"Product with barcode '{barcode}' not found. Please add the product first.")
        return barcode