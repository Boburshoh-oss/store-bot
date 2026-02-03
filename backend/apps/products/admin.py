from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at', 'updated_at']
    search_fields = ['name', 'description']
    list_filter = ['created_at']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'barcode', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'barcode']
    list_filter = ['category', 'is_active', 'created_at']
    list_editable = ['is_active']
