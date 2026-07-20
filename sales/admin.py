from django.contrib import admin
from .models import Sale, SaleItem

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price', 'subtotal')
    can_delete = False

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'total_amount', 'performed_by', 'created_at')
    list_filter = ('created_at', 'performed_by')
    search_fields = ('id', 'performed_by__username')
    readonly_fields = ('total_amount', 'created_at', 'updated_at')
    inlines = [SaleItemInline]
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    fieldsets = (
        ('Sale Information', {
            'fields': ('total_amount', 'performed_by')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ('sale', 'product', 'quantity', 'price', 'subtotal')
    list_filter = ('sale__created_at', 'product')
    search_fields = ('product__name', 'product__barcode')
    readonly_fields = ('subtotal',)