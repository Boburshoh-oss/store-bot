from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WarehouseViewSet, StockViewSet, StockMovementViewSet

router = DefaultRouter()
router.register(r'warehouses', WarehouseViewSet, basename='warehouse')
router.register(r'stocks', StockViewSet, basename='stock')
router.register(r'movements', StockMovementViewSet, basename='movement')

urlpatterns = [
    path('', include(router.urls)),
]
