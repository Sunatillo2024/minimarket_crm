from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from .models import Expense
from .forms import ExpenseForm

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.profile.role == 'admin'
    
    def handle_no_permission(self):
        messages.error(self.request, "You don't have permission to access this page.")
        return redirect('reports:dashboard')

class ExpenseListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = Expense
    template_name = 'expenses/list.html'
    context_object_name = 'expenses'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(description__icontains=search)
        return queryset

class ExpenseCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'expenses/form.html'
    success_url = reverse_lazy('expenses:list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, f"Expense '{self.object.get_category_display()}' added successfully.")
        return response

class ExpenseUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'expenses/form.html'
    success_url = reverse_lazy('expenses:list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Expense updated successfully.")
        return response

class ExpenseDeleteView(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    model = Expense
    template_name = 'expenses/confirm_delete.html'
    success_url = reverse_lazy('expenses:list')

    def delete(self, request, *args, **kwargs):
        expense = self.get_object()
        messages.success(request, f"Expense '{expense.get_category_display()}' deleted successfully.")
        return super().delete(request, *args, **kwargs)