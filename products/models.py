from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name

class Product(models.Model):
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('out_of_stock', 'Out of Stock'),
        ('discontinued', 'Discontinued'),
    )
    barcode = models.CharField(max_length=50, unique=True, db_index=True, help_text="Scan barcode or enter manually")
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    buy_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    sell_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    current_stock = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['barcode']),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return f"{self.name} ({self.barcode})"

    def is_low_stock(self, threshold=5):
        return self.current_stock <= threshold

    def update_stock(self, quantity):
        """Increase or decrease stock (quantity can be negative)"""
        self.current_stock = max(0, self.current_stock + quantity)
        self.save()
        # Update status automatically
        if self.current_stock == 0:
            self.status = 'out_of_stock'
        else:
            self.status = 'available'
        self.save()
        
        
