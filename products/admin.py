from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('barcode', 'name', 'category', 'buy_price', 'sell_price', 'current_stock', 'status')
    list_filter = ('category', 'status')
    search_fields = ('barcode', 'name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('barcode', 'name', 'category', 'image')
        }),
        ('Pricing', {
            'fields': ('buy_price', 'sell_price')
        }),
        ('Inventory', {
            'fields': ('current_stock', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )