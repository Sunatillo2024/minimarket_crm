from django.db import models
from django.contrib.auth.models import User
from datetime import date

class Expense(models.Model):
    CATEGORY_CHOICES = (
        ('electricity', 'Electricity'),
        ('internet', 'Internet'),
        ('transport', 'Transport'),
        ('rent', 'Rent'),
        ('salary', 'Salary'),
        ('supplies', 'Supplies'),
        ('maintenance', 'Maintenance'),
        ('other', 'Other'),
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=date.today)  # editable, defaults to today
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='expenses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = 'Expense'
        verbose_name_plural = 'Expenses'

    def __str__(self):
        return f"{self.get_category_display()} - {self.amount} ({self.date.strftime('%Y-%m-%d')})"