from django.db import models
from django.utils import timezone


class UserRole(models.TextChoices):
    """Foydalanuvchi rollari"""

    ADMIN = "admin", "Admin"
    WAREHOUSE = "warehouse", "Ombor hodimi"
    REQUESTER = "requester", "Zakas qiluvchi"


class OrderStatus(models.TextChoices):
    """Zakas holatlari"""

    PENDING = "pending", "Kutilmoqda"
    COMPLETED = "completed", "Bajarildi"
    CANCELLED = "cancelled", "Bekor qilindi"


class TransactionType(models.TextChoices):
    """Tranzaksiya turlari"""

    IN = "in", "Kirim"
    OUT = "out", "Chiqim"


class TelegramUser(models.Model):
    """Telegram foydalanuvchisi"""

    telegram_id = models.BigIntegerField(unique=True, verbose_name="Telegram ID")
    username = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Username"
    )
    full_name = models.CharField(max_length=255, verbose_name="To'liq ism")
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.REQUESTER,
        verbose_name="Rol",
    )
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Ro'yxatdan o'tgan sana"
    )

    class Meta:
        verbose_name = "Telegram foydalanuvchi"
        verbose_name_plural = "Telegram foydalanuvchilar"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN

    @property
    def is_warehouse(self):
        return self.role in [UserRole.ADMIN, UserRole.WAREHOUSE]

    @property
    def is_requester(self):
        return self.role == UserRole.REQUESTER


class Category(models.Model):
    """Mahsulot kategoriyasi"""

    name = models.CharField(max_length=255, unique=True, verbose_name="Nomi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    """Mahsulot"""

    UNIT_CHOICES = [
        ("kg", "Kilogramm"),
        ("g", "Gramm"),
        ("l", "Litr"),
        ("ml", "Millilitr"),
        ("dona", "Dona"),
        ("paket", "Paket"),
        ("quti", "Quti"),
        ("bochka", "Bo'lak"),
    ]

    name = models.CharField(max_length=255, verbose_name="Nomi")
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name="Kategoriya",
    )
    quantity = models.DecimalField(
        max_digits=10, decimal_places=2, default=0, verbose_name="Joriy miqdor"
    )
    unit = models.CharField(
        max_length=20,
        choices=UNIT_CHOICES,
        default="dona",
        verbose_name="O'lchov birligi",
    )
    min_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="Minimum miqdor",
        help_text="Bu miqdordan kam bo'lsa ogohlantirish yuboriladi",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan sana")

    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"
        ordering = ["category", "name"]
        unique_together = ["name", "category"]

    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit})"

    @property
    def is_low_stock(self):
        """Mahsulot kam qoldimi?"""
        return self.quantity <= self.min_quantity and self.min_quantity > 0


class Order(models.Model):
    """Zakas"""

    requester = models.ForeignKey(
        TelegramUser,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Zakas qiluvchi",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Mahsulot",
    )
    quantity = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Miqdor"
    )
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        verbose_name="Holat",
    )
    fulfilled_by = models.ForeignKey(
        TelegramUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fulfilled_orders",
        verbose_name="Bajargan hodim",
    )
    note = models.TextField(blank=True, null=True, verbose_name="Izoh")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan sana")
    fulfilled_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Bajarilgan sana"
    )

    class Meta:
        verbose_name = "Zakas"
        verbose_name_plural = "Zakaslar"
        ordering = ["-created_at"]

    def __str__(self):
        return f"#{self.id} - {self.product.name} ({self.quantity} {self.product.unit})"

    def complete(self, fulfilled_by: TelegramUser):
        """Zakasni bajarish"""
        self.status = OrderStatus.COMPLETED
        self.fulfilled_by = fulfilled_by
        self.fulfilled_at = timezone.now()
        self.save()

    def cancel(self):
        """Zakasni bekor qilish"""
        self.status = OrderStatus.CANCELLED
        self.save()


class Transaction(models.Model):
    """Kirim-chiqim tarixi"""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="transactions",
        verbose_name="Mahsulot",
    )
    transaction_type = models.CharField(
        max_length=10, choices=TransactionType.choices, verbose_name="Turi"
    )
    quantity = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Miqdor"
    )
    performed_by = models.ForeignKey(
        TelegramUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="transactions",
        verbose_name="Bajargan",
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
        verbose_name="Zakas",
    )
    note = models.TextField(blank=True, null=True, verbose_name="Izoh")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Sana")

    class Meta:
        verbose_name = "Tranzaksiya"
        verbose_name_plural = "Tranzaksiyalar"
        ordering = ["-created_at"]

    def __str__(self):
        type_symbol = "+" if self.transaction_type == TransactionType.IN else "-"
        return f"{type_symbol}{self.quantity} {self.product.unit} {self.product.name}"
