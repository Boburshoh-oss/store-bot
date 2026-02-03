from django.db import models


class Category(models.Model):
    """Mahsulot kategoriyasi / Product category"""
    name = models.CharField(max_length=255, verbose_name="Nomi")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqti")

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Product(models.Model):
    """Mahsulot / Product"""
    name = models.CharField(max_length=255, verbose_name="Nomi")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='products',
        verbose_name="Kategoriya"
    )
    price = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        verbose_name="Narxi"
    )
    image = models.ImageField(
        upload_to='products/images/', 
        blank=True, 
        null=True,
        verbose_name="Rasm"
    )
    barcode = models.CharField(
        max_length=100, 
        blank=True, 
        unique=True, 
        null=True,
        verbose_name="Shtrix-kod"
    )
    is_active = models.BooleanField(default=True, verbose_name="Faolmi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqti")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqti")

    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"
        ordering = ['-created_at']

    def __str__(self):
        return self.name
