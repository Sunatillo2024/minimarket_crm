from django import forms
from products.models import Product

class POSAddItemForm(forms.Form):
    barcode = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Scan barcode',
            'autofocus': True,
            'id': 'barcode-input',
        }),
        label=''
    )

    def clean_barcode(self):
        barcode = self.cleaned_data.get('barcode')
        try:
            product = Product.objects.get(barcode=barcode)
            if product.current_stock <= 0:
                raise forms.ValidationError(f"Product '{product.name}' is out of stock.")
        except Product.DoesNotExist:
            raise forms.ValidationError(f"Product with barcode '{barcode}' not found.")
        return barcode

class PaymentForm(forms.Form):
    amount_paid = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Amount received',
            'step': '0.01',
        }),
        label='Amount Paid'
    )