from rest_framework import serializers
from .models import Warehouse, Stock, StockMovement


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = ['id', 'name', 'location', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class StockSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Stock
        fields = [
            'id', 'product', 'product_name', 'warehouse', 'warehouse_name',
            'quantity', 'min_quantity', 'is_low_stock',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class StockMovementSerializer(serializers.ModelSerializer):
    stock_info = serializers.SerializerMethodField()
    
    class Meta:
        model = StockMovement
        fields = [
            'id', 'stock', 'stock_info', 'movement_type',
            'quantity', 'note', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_stock_info(self, obj):
        """
        Get stock information for the movement.
        Note: This method requires the queryset to use select_related('stock__product', 'stock__warehouse')
        to avoid N+1 queries. This is already configured in StockMovementViewSet.
        """
        return {
            'product': obj.stock.product.name,
            'warehouse': obj.stock.warehouse.name,
            'current_quantity': obj.stock.quantity
        }
