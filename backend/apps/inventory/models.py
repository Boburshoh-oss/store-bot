from django.db import models
from apps.products.models import Product


class Warehouse(models.Model):
    """Ombor / Warehouse"""
    name = models.CharField(max_length=255, verbose_name="Nomi")
    location = models.TextField(blank=True, verbose_name="Manzil")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqti")

    class Meta:
        verbose_name = "Ombor"
        verbose_name_plural = "Omborlar"
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Stock(models.Model):
    """Mahsulot qoldig'i / Product stock"""
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='stocks',
        verbose_name="Mahsulot"
    )
    warehouse = models.ForeignKey(
        Warehouse, 
        on_delete=models.CASCADE, 
        related_name='stocks',
        verbose_name="Ombor"
    )
    quantity = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        verbose_name="Miqdori"
    )
    min_quantity = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=0,
        verbose_name="Minimal miqdor"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqti")

    class Meta:
        verbose_name = "Qoldiq"
        verbose_name_plural = "Qoldiqlar"
        ordering = ['-updated_at']
        unique_together = ['product', 'warehouse']

    def __str__(self):
        return f"{self.product.name} - {self.warehouse.name}: {self.quantity}"

    @property
    def is_low_stock(self):
        """Qoldiq kammi / Is stock low"""
        return self.quantity <= self.min_quantity


class StockMovement(models.Model):
    """Mahsulot harakati / Stock movement"""
    MOVEMENT_TYPE_CHOICES = [
        ('IN', 'Kirish / Income'),
        ('OUT', 'Chiqish / Outcome'),
        ('TRANSFER', "Ko'chirish / Transfer"),
    ]
    
    stock = models.ForeignKey(
        Stock, 
        on_delete=models.CASCADE, 
        related_name='movements',
        verbose_name="Qoldiq"
    )
    movement_type = models.CharField(
        max_length=10, 
        choices=MOVEMENT_TYPE_CHOICES,
        verbose_name="Harakat turi"
    )
    quantity = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        verbose_name="Miqdori"
    )
    note = models.TextField(blank=True, verbose_name="Izoh")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")

    class Meta:
        verbose_name = "Harakat"
        verbose_name_plural = "Harakatlar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.stock.product.name} - {self.movement_type}: {self.quantity}"
