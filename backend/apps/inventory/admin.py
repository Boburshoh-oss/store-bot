from django.contrib import admin
from .models import TelegramUser, Category, Product, Order, Transaction


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = [
        "telegram_id",
        "full_name",
        "username",
        "role",
        "is_active",
        "created_at",
    ]
    list_filter = ["role", "is_active"]
    search_fields = ["telegram_id", "full_name", "username"]
    list_editable = ["role", "is_active"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]
    search_fields = ["name"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "category",
        "quantity",
        "unit",
        "min_quantity",
        "is_low_stock",
        "updated_at",
    ]
    list_filter = ["category", "unit"]
    search_fields = ["name"]
    list_editable = ["quantity", "min_quantity"]

    def is_low_stock(self, obj):
        return obj.is_low_stock

    is_low_stock.boolean = True
    is_low_stock.short_description = "Kam qoldimi?"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "requester",
        "product",
        "quantity",
        "status",
        "fulfilled_by",
        "created_at",
        "fulfilled_at",
    ]
    list_filter = ["status", "created_at"]
    search_fields = ["requester__full_name", "product__name"]
    raw_id_fields = ["requester", "product", "fulfilled_by"]


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "product",
        "transaction_type",
        "quantity",
        "performed_by",
        "order",
        "created_at",
    ]
    list_filter = ["transaction_type", "created_at"]
    search_fields = ["product__name", "performed_by__full_name"]
    raw_id_fields = ["product", "performed_by", "order"]
