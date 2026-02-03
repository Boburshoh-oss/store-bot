from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from .models import Warehouse, Stock, StockMovement
from .serializers import WarehouseSerializer, StockSerializer, StockMovementSerializer


class WarehouseViewSet(viewsets.ModelViewSet):
    queryset = Warehouse.objects.all()
    serializer_class = WarehouseSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'location']
    ordering_fields = ['name', 'created_at']


class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.select_related('product', 'warehouse').all()
    serializer_class = StockSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product', 'warehouse']
    search_fields = ['product__name', 'warehouse__name']
    ordering_fields = ['quantity', 'updated_at']

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Kam qoldiqlar / Low stock items"""
        from django.db.models import F
        low_stocks = self.get_queryset().filter(quantity__lte=F('min_quantity'))
        serializer = self.get_serializer(low_stocks, many=True)
        return Response(serializer.data)


class StockMovementViewSet(viewsets.ModelViewSet):
    queryset = StockMovement.objects.select_related('stock__product', 'stock__warehouse').all()
    serializer_class = StockMovementSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['stock', 'movement_type']
    search_fields = ['stock__product__name', 'note']
    ordering_fields = ['created_at']

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """Harakat yaratish va qoldiqni yangilash / Create movement and update stock"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        movement = serializer.save()
        stock = movement.stock
        
        # Qoldiqni yangilash / Update stock quantity
        if movement.movement_type == 'IN':
            stock.quantity += movement.quantity
        elif movement.movement_type == 'OUT':
            if stock.quantity < movement.quantity:
                return Response(
                    {'error': 'Qoldiq yetarli emas / Insufficient stock'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            stock.quantity -= movement.quantity
        
        stock.save()
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
