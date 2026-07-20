from django.views.generic import TemplateView, ListView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from .forms import POSAddItemForm, PaymentForm
from .models import Sale, SaleItem
from products.models import Product
from decimal import Decimal

class POSView(LoginRequiredMixin, TemplateView):
    template_name = 'sales/pos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get cart from session
        cart = self.request.session.get('pos_cart', [])
        # Enrich cart with product details
        cart_items = []
        total = Decimal('0.00')
        for item in cart:
            product = get_object_or_404(Product, id=item['product_id'])
            subtotal = product.sell_price * item['quantity']
            cart_items.append({
                'product': product,
                'quantity': item['quantity'],
                'subtotal': subtotal,
            })
            total += subtotal
        context['cart_items'] = cart_items
        context['total'] = total
        context['add_form'] = POSAddItemForm()
        context['payment_form'] = PaymentForm()
        return context

class AddItemView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        form = POSAddItemForm(request.POST)
        if form.is_valid():
            barcode = form.cleaned_data['barcode']
            product = Product.objects.get(barcode=barcode)
            # Get cart from session
            cart = request.session.get('pos_cart', [])
            # Check if product already in cart
            found = False
            for item in cart:
                if item['product_id'] == product.id:
                    # Check stock availability
                    if product.current_stock < item['quantity'] + 1:
                        messages.error(request, f"Not enough stock for '{product.name}'. Available: {product.current_stock}")
                        return redirect('sales:pos')
                    item['quantity'] += 1
                    found = True
                    break
            if not found:
                # Check if at least one in stock
                if product.current_stock < 1:
                    messages.error(request, f"Product '{product.name}' is out of stock.")
                    return redirect('sales:pos')
                cart.append({'product_id': product.id, 'quantity': 1})
            # Save cart to session
            request.session['pos_cart'] = cart
            messages.success(request, f"Added '{product.name}' to cart.")
        else:
            # Form errors will contain validation messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
        return redirect('sales:pos')

class RemoveItemView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        product_id = kwargs.get('product_id')
        cart = request.session.get('pos_cart', [])
        for i, item in enumerate(cart):
            if item['product_id'] == product_id:
                if item['quantity'] > 1:
                    item['quantity'] -= 1
                else:
                    cart.pop(i)
                break
        request.session['pos_cart'] = cart
        messages.success(request, "Cart updated.")
        return redirect('sales:pos')

class ClearCartView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        if 'pos_cart' in request.session:
            del request.session['pos_cart']
        messages.info(request, "Cart cleared.")
        return redirect('sales:pos')

class CompleteSaleView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        cart = request.session.get('pos_cart', [])
        if not cart:
            messages.error(request, "Cart is empty.")
            return redirect('sales:pos')
        
        payment_form = PaymentForm(request.POST)
        if not payment_form.is_valid():
            messages.error(request, "Please enter a valid payment amount.")
            return redirect('sales:pos')
        
        # Calculate total
        total = Decimal('0.00')
        cart_items = []
        for item in cart:
            product = get_object_or_404(Product, id=item['product_id'])
            # Check stock availability
            if product.current_stock < item['quantity']:
                messages.error(request, f"Not enough stock for '{product.name}'. Available: {product.current_stock}")
                return redirect('sales:pos')
            subtotal = product.sell_price * item['quantity']
            total += subtotal
            cart_items.append({
                'product': product,
                'quantity': item['quantity'],
                'price': product.sell_price,
                'subtotal': subtotal,
            })
        
        amount_paid = payment_form.cleaned_data['amount_paid']
        if amount_paid < total:
            messages.error(request, f"Insufficient payment. Total is {total}, you paid {amount_paid}.")
            return redirect('sales:pos')
        
        # Create sale
        sale = Sale.objects.create(
            total_amount=total,
            performed_by=request.user,
        )
        # Create sale items and update stock
        for item in cart_items:
            SaleItem.objects.create(
                sale=sale,
                product=item['product'],
                quantity=item['quantity'],
                price=item['price'],
                subtotal=item['subtotal'],
            )
            # Decrease stock
            item['product'].update_stock(-item['quantity'])
        
        # Clear cart
        del request.session['pos_cart']
        messages.success(request, f"Sale completed! Total: {total}, Change: {amount_paid - total}")
        return redirect('sales:pos')

class TodaySalesView(LoginRequiredMixin, ListView):
    model = Sale
    template_name = 'sales/today.html'
    context_object_name = 'sales'
    paginate_by = 20

    def get_queryset(self):
        today = timezone.now().date()
        return Sale.objects.filter(created_at__date=today).order_by('-created_at')