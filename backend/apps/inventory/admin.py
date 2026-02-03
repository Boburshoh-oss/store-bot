from django.contrib import admin
from .models import Warehouse, Stock, StockMovement


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'created_at', 'updated_at']
    search_fields = ['name', 'location']
    list_filter = ['created_at']


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['product', 'warehouse', 'quantity', 'min_quantity', 'low_stock_indicator', 'updated_at']
    search_fields = ['product__name', 'warehouse__name']
    list_filter = ['warehouse', 'updated_at']
    
    def low_stock_indicator(self, obj):
        """Display low stock indicator efficiently"""
        return '⚠️' if obj.quantity <= obj.min_quantity else '✅'
    low_stock_indicator.short_description = 'Status'


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['stock', 'movement_type', 'quantity', 'created_at']
    search_fields = ['stock__product__name', 'note']
    list_filter = ['movement_type', 'created_at']
