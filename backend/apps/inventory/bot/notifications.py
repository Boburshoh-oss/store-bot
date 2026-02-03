"""Bildirishnomalar tizimi"""

from telegram import Bot

from apps.inventory.models import Order, Product, TelegramUser, UserRole


async def notify_new_order(bot: Bot, order: Order, requester: TelegramUser):
    """Yangi zakas haqida ombor hodimlariga xabar yuborish"""

    # Barcha ombor hodimlarini olish
    warehouse_users = TelegramUser.objects.filter(
        role__in=[UserRole.ADMIN, UserRole.WAREHOUSE], is_active=True
    ).exclude(telegram_id=requester.telegram_id)

    message = (
        f"🔔 <b>YANGI ZAKAS!</b>\n\n"
        f"📋 Zakas: #{order.id}\n"
        f"👤 Kimdan: {requester.full_name}\n"
        f"📦 Mahsulot: {order.product.name}\n"
        f"📊 Miqdor: {order.quantity} {order.product.unit}\n"
        f"📅 Sana: {order.created_at.strftime('%d.%m.%Y %H:%M')}"
    )

    if order.note:
        message += f"\n📝 Izoh: {order.note}"

    message += "\n\n📥 Zakaslarni ko'rish: /orders"

    for user in warehouse_users:
        try:
            await bot.send_message(
                chat_id=user.telegram_id, text=message, parse_mode="HTML"
            )
        except Exception as e:
            # Foydalanuvchi botni bloklagan yoki boshqa xatolik
            print(f"Xabar yuborishda xatolik (user_id={user.telegram_id}): {e}")


async def notify_low_stock(bot: Bot, product: Product):
    """Mahsulot kam qolganda ombor hodimlariga ogohlantirish"""

    # Barcha ombor hodimlarini olish
    warehouse_users = TelegramUser.objects.filter(
        role__in=[UserRole.ADMIN, UserRole.WAREHOUSE], is_active=True
    )

    message = (
        f"⚠️ <b>OGOHLANTIRISH: Mahsulot kam qoldi!</b>\n\n"
        f"📦 Mahsulot: {product.name}\n"
        f"📁 Kategoriya: {product.category.name}\n"
        f"📊 Qolgan miqdor: {product.quantity} {product.unit}\n"
        f"📉 Minimum: {product.min_quantity} {product.unit}\n\n"
        f"➕ Mahsulot qo'shish: /add"
    )

    for user in warehouse_users:
        try:
            await bot.send_message(
                chat_id=user.telegram_id, text=message, parse_mode="HTML"
            )
        except Exception as e:
            print(f"Xabar yuborishda xatolik (user_id={user.telegram_id}): {e}")


async def notify_order_completed(bot: Bot, order: Order):
    """Zakas bajarilganda zakas qiluvchiga xabar"""
    try:
        message = (
            f"✅ <b>Zakasngiz bajarildi!</b>\n\n"
            f"📋 Zakas: #{order.id}\n"
            f"📦 Mahsulot: {order.product.name}\n"
            f"📊 Miqdor: {order.quantity} {order.product.unit}\n"
            f"👤 Bergan: {order.fulfilled_by.full_name if order.fulfilled_by else 'Noma\'lum'}\n"
            f"📅 Bajarilgan: {order.fulfilled_at.strftime('%d.%m.%Y %H:%M') if order.fulfilled_at else ''}"
        )

        await bot.send_message(
            chat_id=order.requester.telegram_id, text=message, parse_mode="HTML"
        )
    except Exception as e:
        print(f"Xabar yuborishda xatolik: {e}")


async def notify_order_cancelled(bot: Bot, order: Order, reason: str = None):
    """Zakas bekor qilinganda zakas qiluvchiga xabar"""
    try:
        message = (
            f"❌ <b>Zakasngiz bekor qilindi</b>\n\n"
            f"📋 Zakas: #{order.id}\n"
            f"📦 Mahsulot: {order.product.name}\n"
            f"📊 Miqdor: {order.quantity} {order.product.unit}"
        )

        if reason:
            message += f"\n📝 Sabab: {reason}"

        await bot.send_message(
            chat_id=order.requester.telegram_id, text=message, parse_mode="HTML"
        )
    except Exception as e:
        print(f"Xabar yuborishda xatolik: {e}")
