"""Admin handlerlari"""

from telegram import Update
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
)

from apps.inventory.models import TelegramUser, UserRole
from apps.inventory.bot.decorators import admin_required, get_or_create_user
from apps.inventory.bot.keyboards import (
    get_main_menu_keyboard,
    get_users_keyboard,
    get_user_actions_keyboard,
)


# ============ Users Handler ============


@admin_required
async def users_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchilar ro'yxati"""
    total = TelegramUser.objects.count()

    await update.message.reply_text(
        f"👥 <b>Foydalanuvchilar: {total} ta</b>\n\n"
        f"👑 Admin | 📦 Ombor hodimi | 👤 Zakas qiluvchi\n"
        f"🟢 Faol | 🔴 Bloklangan",
        parse_mode="HTML",
        reply_markup=get_users_keyboard(),
    )


async def users_page_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchilar sahifasi"""
    query = update.callback_query
    await query.answer()

    page = int(query.data.split(":")[1])
    total = TelegramUser.objects.count()

    await query.edit_message_text(
        f"👥 <b>Foydalanuvchilar: {total} ta</b>\n\n"
        f"👑 Admin | 📦 Ombor hodimi | 👤 Zakas qiluvchi\n"
        f"🟢 Faol | 🔴 Bloklangan",
        parse_mode="HTML",
        reply_markup=get_users_keyboard(page),
    )


async def user_detail_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi ma'lumotlari"""
    query = update.callback_query
    await query.answer()

    if query.data == "back_to_users":
        total = TelegramUser.objects.count()
        await query.edit_message_text(
            f"👥 <b>Foydalanuvchilar: {total} ta</b>\n\n"
            f"👑 Admin | 📦 Ombor hodimi | 👤 Zakas qiluvchi\n"
            f"🟢 Faol | 🔴 Bloklangan",
            parse_mode="HTML",
            reply_markup=get_users_keyboard(),
        )
        return

    user_id = int(query.data.split(":")[1])

    try:
        user = TelegramUser.objects.get(id=user_id)

        status = "🟢 Faol" if user.is_active else "🔴 Bloklangan"
        role_emoji = (
            "👑"
            if user.role == UserRole.ADMIN
            else "📦" if user.role == UserRole.WAREHOUSE else "👤"
        )

        # Statistika
        orders_count = user.orders.count()
        completed_orders = user.orders.filter(status="completed").count()

        text = (
            f"👤 <b>{user.full_name}</b>\n\n"
            f"🆔 Telegram ID: <code>{user.telegram_id}</code>\n"
            f"📱 Username: @{user.username or 'yo\'q'}\n"
            f"{role_emoji} Rol: {user.get_role_display()}\n"
            f"{status}\n"
            f"📅 Ro'yxatdan: {user.created_at.strftime('%d.%m.%Y')}\n\n"
            f"📊 Statistika:\n"
            f"📦 Zakaslar: {orders_count} ta\n"
            f"✅ Bajarilgan: {completed_orders} ta"
        )

        await query.edit_message_text(
            text,
            parse_mode="HTML",
            reply_markup=get_user_actions_keyboard(user_id, user.role, user.is_active),
        )
    except TelegramUser.DoesNotExist:
        await query.edit_message_text("❌ Foydalanuvchi topilmadi.")


async def set_role_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Rol o'zgartirish"""
    query = update.callback_query
    current_user = get_or_create_user(update)

    parts = query.data.split(":")
    user_id = int(parts[1])
    new_role = parts[2]

    try:
        user = TelegramUser.objects.get(id=user_id)

        # O'zini o'zgartirish mumkin emas
        if user.telegram_id == current_user.telegram_id:
            await query.answer(
                "O'zingizning rolingizni o'zgartira olmaysiz!", show_alert=True
            )
            return

        old_role = user.get_role_display()
        user.role = new_role
        user.save()

        await query.answer(f"✅ Rol o'zgartirildi: {user.get_role_display()}")

        # Foydalanuvchiga xabar
        try:
            role_text = user.get_role_display()
            await context.bot.send_message(
                chat_id=user.telegram_id,
                text=f"🔔 Sizning rolingiz o'zgartirildi!\n\n"
                f"Eski rol: {old_role}\n"
                f"Yangi rol: {role_text}\n\n"
                f"Yangi imkoniyatlarni ko'rish uchun /start buyrug'ini yuboring.",
            )
        except Exception:
            pass

        # Sahifani yangilash
        await user_detail_callback(update, context)

    except TelegramUser.DoesNotExist:
        await query.answer("❌ Foydalanuvchi topilmadi.", show_alert=True)


async def block_user_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchini bloklash"""
    query = update.callback_query
    current_user = get_or_create_user(update)

    user_id = int(query.data.split(":")[1])

    try:
        user = TelegramUser.objects.get(id=user_id)

        if user.telegram_id == current_user.telegram_id:
            await query.answer("O'zingizni bloklay olmaysiz!", show_alert=True)
            return

        user.is_active = False
        user.save()

        await query.answer("🔴 Foydalanuvchi bloklandi!")

        # Foydalanuvchiga xabar
        try:
            await context.bot.send_message(
                chat_id=user.telegram_id,
                text="⛔ Sizning hisobingiz bloklandi. Admin bilan bog'laning.",
            )
        except Exception:
            pass

        # Sahifani yangilash
        await user_detail_callback(update, context)

    except TelegramUser.DoesNotExist:
        await query.answer("❌ Foydalanuvchi topilmadi.", show_alert=True)


async def unblock_user_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchini aktivlashtirish"""
    query = update.callback_query

    user_id = int(query.data.split(":")[1])

    try:
        user = TelegramUser.objects.get(id=user_id)
        user.is_active = True
        user.save()

        await query.answer("🟢 Foydalanuvchi aktivlashtirildi!")

        # Foydalanuvchiga xabar
        try:
            await context.bot.send_message(
                chat_id=user.telegram_id,
                text="✅ Sizning hisobingiz qayta aktivlashtirildi!\n\n"
                "Botdan foydalanish uchun /start buyrug'ini yuboring.",
            )
        except Exception:
            pass

        # Sahifani yangilash
        await user_detail_callback(update, context)

    except TelegramUser.DoesNotExist:
        await query.answer("❌ Foydalanuvchi topilmadi.", show_alert=True)


# ============ Create Handlers ============

users_handler = CommandHandler("users", users_command)
set_role_handler = None  # CallbackQueryHandler orqali boshqariladi
