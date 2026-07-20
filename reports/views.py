from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Q
from django.utils import timezone
from sales.models import Sale, SaleItem
from expenses.models import Expense
from products.models import Product
from decimal import Decimal

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()

        # Today's Sales
        today_sales = Sale.objects.filter(created_at__date=today)
        total_sales = today_sales.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

        # Today's Profit (based on current buy price)
        total_profit = Decimal('0.00')
        for sale in today_sales:
            for item in sale.items.all():
                # Get current buy price from product (simplified)
                buy_price = item.product.buy_price
                profit_per_unit = item.price - buy_price
                total_profit += profit_per_unit * item.quantity

        # Today's Expenses
        total_expenses = Expense.objects.filter(date=today).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        # Net Profit
        net_profit = total_profit - total_expenses

        # Current Inventory Value
        products = Product.objects.all()
        inventory_value = sum(p.buy_price * p.current_stock for p in products)

        # Low Stock Products (threshold <=5)
        low_stock_products = Product.objects.filter(current_stock__lte=5, current_stock__gt=0)
        out_of_stock_products = Product.objects.filter(current_stock=0)

        context.update({
            'today_sales': total_sales,
            'today_profit': total_profit,
            'today_expenses': total_expenses,
            'net_profit': net_profit,
            'inventory_value': inventory_value,
            'low_stock_products': low_stock_products,
            'out_of_stock_products': out_of_stock_products,
            'total_products': products.count(),
        })
        return context