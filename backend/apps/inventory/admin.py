from django.contrib import admin
from .models import Warehouse, Stock, StockMovement


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ['name', 'location', 'created_at', 'updated_at']
    search_fields = ['name', 'location']
    list_filter = ['created_at']


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['product', 'warehouse', 'quantity', 'min_quantity', 'is_low_stock', 'updated_at']
    search_fields = ['product__name', 'warehouse__name']
    list_filter = ['warehouse', 'updated_at']
    readonly_fields = ['is_low_stock']


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['stock', 'movement_type', 'quantity', 'created_at']
    search_fields = ['stock__product__name', 'note']
    list_filter = ['movement_type', 'created_at']
