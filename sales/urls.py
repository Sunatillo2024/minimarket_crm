from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('pos/', views.POSView.as_view(), name='pos'),
    path('pos/add/', views.AddItemView.as_view(), name='add_item'),
    path('pos/remove/<int:product_id>/', views.RemoveItemView.as_view(), name='remove_item'),
    path('pos/clear/', views.ClearCartView.as_view(), name='clear_cart'),
    path('pos/complete/', views.CompleteSaleView.as_view(), name='complete_sale'),
    path('today/', views.TodaySalesView.as_view(), name='today'),
]