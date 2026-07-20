from django.views.generic import ListView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from .models import InventoryTransaction
from .forms import InventoryAddForm

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.profile.role == 'admin'
    
    def handle_no_permission(self):
        messages.error(self.request, "You don't have permission to access this page.")
        return redirect('reports:dashboard')

class InventoryListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = InventoryTransaction
    template_name = 'inventory/list.html'
    context_object_name = 'transactions'
    paginate_by = 20
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(product__name__icontains=search) |
                models.Q(product__barcode__icontains=search) |
                models.Q(note__icontains=search)
            )
        return queryset

class InventoryAddView(LoginRequiredMixin, AdminRequiredMixin, FormView):
    template_name = 'inventory/add.html'
    form_class = InventoryAddForm
    success_url = reverse_lazy('inventory:list')

    def form_valid(self, form):
        barcode = form.cleaned_data['barcode']
        quantity = form.cleaned_data['quantity']
        note = form.cleaned_data.get('note', '')

        try:
            product = Product.objects.get(barcode=barcode)
        except Product.DoesNotExist:
            messages.error(self.request, f"Product with barcode '{barcode}' not found.")
            return self.form_invalid(form)

        # Increase stock
        product.update_stock(quantity)

        # Create transaction record
        InventoryTransaction.objects.create(
            product=product,
            transaction_type='IN',
            quantity=quantity,
            note=note,
            performed_by=self.request.user
        )

        messages.success(self.request, f"Added {quantity} units of '{product.name}' to inventory.")
        return super().form_valid(form)