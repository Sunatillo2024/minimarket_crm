"""
URL configuration for minimarket_crm project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Accounts (login, logout)
    path('accounts/', include('accounts.urls')),
    # Products app
    path('products/', include('products.urls')),
    # Inventory app
    path('inventory/', include('inventory.urls')),
    # Sales app
    path('sales/', include('sales.urls')),
    # Expenses app
    path('expenses/', include('expenses.urls')),
    # Reports app (dashboard)
    path('', include('reports.urls')),  # empty path for dashboard
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)