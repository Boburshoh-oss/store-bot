"""Yordamchi funksiyalar"""

from decimal import Decimal, InvalidOperation
from typing import Optional, Tuple, List

from apps.inventory.models import (
    Product,
    Category,
    Order,
    Transaction,
    TransactionType,
    TelegramUser,
    OrderStatus,
    UserRole,
)


def parse_quantity(text: str) -> Tuple[bool, Optional[Decimal], str]:
    """Miqdorni parsing qilish

    Returns:
        (success, quantity, error_message)
    """
    try:
        # Vergulni nuqtaga almashtirish
        text = text.replace(",", ".").strip()
        quantity = Decimal(text)

        if quantity <= 0:
            return False, None, "Miqdor 0 dan katta bo'lishi kerak."

        if quantity > 999999:
            return False, None, "Miqdor juda katta."

        return True, quantity, ""
    except (InvalidOperation, ValueError):
        return False, None, "Noto'g'ri format. Masalan: 5 yoki 2.5"


def add_product_stock(
    product: Product, quantity: Decimal, user: TelegramUser, note: str = None
) -> Transaction:
    """Mahsulot qo'shish (kirim)"""
    product.quantity += quantity
    product.save()

    transaction = Transaction.objects.create(
        product=product,
        transaction_type=TransactionType.IN,
        quantity=quantity,
        performed_by=user,
        note=note,
    )

    return transaction


def remove_product_stock(
    product: Product,
    quantity: Decimal,
    user: TelegramUser,
    order: Order = None,
    note: str = None,
) -> Tuple[bool, Optional[Transaction], str]:
    """Mahsulot chiqarish

    Returns:
        (success, transaction, error_message)
    """
    if product.quantity < quantity:
        return (
            False,
            None,
            f"Yetarli mahsulot yo'q. Mavjud: {product.quantity} {product.unit}",
        )

    product.quantity -= quantity
    product.save()

    transaction = Transaction.objects.create(
        product=product,
        transaction_type=TransactionType.OUT,
        quantity=quantity,
        performed_by=user,
        order=order,
        note=note,
    )

    return True, transaction, ""


def format_product_list(products) -> str:
    """Mahsulotlar ro'yxatini formatlash"""
    if not products:
        return "📭 Mahsulotlar topilmadi."

    # QuerySet bo'lsa, listga o'tkazish
    products = list(products)

    if not products:
        return "📭 Mahsulotlar topilmadi."

    lines = ["📦 <b>Mahsulotlar ro'yxati:</b>\n"]

    current_category = None
    for product in products:
        if current_category != product.category_id:
            current_category = product.category_id
            lines.append(f"\n📁 <b>{product.category.name}</b>")

        # Kam qolgan mahsulotlarni belgilash
        warning = "⚠️ " if product.is_low_stock else ""
        lines.append(f"  {warning}{product.name}: {product.quantity} {product.unit}")

    return "\n".join(lines)


def format_order_info(order: Order) -> str:
    """Zakas ma'lumotlarini formatlash"""
    status_emoji = (
        "⏳"
        if order.status == "pending"
        else "✅" if order.status == "completed" else "❌"
    )

    lines = [
        f"📋 <b>Zakas #{order.id}</b>",
        f"",
        f"📦 Mahsulot: {order.product.name}",
        f"📊 Miqdor: {order.quantity} {order.product.unit}",
        f"👤 Zakas qiluvchi: {order.requester.full_name}",
        f"📅 Sana: {order.created_at.strftime('%d.%m.%Y %H:%M')}",
        f"{status_emoji} Holat: {order.get_status_display()}",
    ]

    if order.fulfilled_by:
        lines.append(f"✅ Bajargan: {order.fulfilled_by.full_name}")

    if order.fulfilled_at:
        lines.append(f"📅 Bajarilgan: {order.fulfilled_at.strftime('%d.%m.%Y %H:%M')}")

    if order.note:
        lines.append(f"📝 Izoh: {order.note}")

    return "\n".join(lines)


def format_transaction_history(transactions, limit: int = 20) -> str:
    """Tranzaksiyalar tarixini formatlash"""
    transactions = list(transactions)[:limit]

    if not transactions:
        return "📭 Tarix bo'sh."

    lines = ["📜 <b>Kirim-chiqim tarixi:</b>\n"]

    for t in transactions:
        type_emoji = "📥" if t.transaction_type == TransactionType.IN else "📤"
        sign = "+" if t.transaction_type == TransactionType.IN else "-"

        line = f"{type_emoji} {sign}{t.quantity} {t.product.unit} {t.product.name}"
        if t.performed_by:
            line += f" ({t.performed_by.full_name})"
        line += f" - {t.created_at.strftime('%d.%m.%Y %H:%M')}"

        lines.append(line)

    return "\n".join(lines)


def get_warehouse_users() -> List[int]:
    """Barcha ombor hodimlarini olish (bildirishnoma uchun)"""
    return list(
        TelegramUser.objects.filter(
            role__in=["admin", "warehouse"], is_active=True
        ).values_list("telegram_id", flat=True)
    )
