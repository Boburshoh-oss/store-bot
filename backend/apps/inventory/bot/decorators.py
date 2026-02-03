"""Rol tekshirish dekoratorlari"""

from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes

from apps.inventory.models import TelegramUser, UserRole


def get_or_create_user(update: Update) -> TelegramUser:
    """Telegram foydalanuvchisini olish yoki yaratish"""
    telegram_user = update.effective_user
    user, created = TelegramUser.objects.get_or_create(
        telegram_id=telegram_user.id,
        defaults={
            "username": telegram_user.username,
            "full_name": telegram_user.full_name
            or telegram_user.first_name
            or "Noma'lum",
        },
    )

    # Agar mavjud bo'lsa, ma'lumotlarni yangilash
    if not created:
        updated = False
        if telegram_user.username and user.username != telegram_user.username:
            user.username = telegram_user.username
            updated = True
        if telegram_user.full_name and user.full_name != telegram_user.full_name:
            user.full_name = telegram_user.full_name
            updated = True
        if updated:
            user.save()

    return user


def authenticated(func):
    """Foydalanuvchi ro'yxatdan o'tganligini tekshirish"""

    @wraps(func)
    async def wrapper(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        user = get_or_create_user(update)

        if not user.is_active:
            await update.message.reply_text(
                "⛔ Sizning hisobingiz bloklangan. Admin bilan bog'laning."
            )
            return

        context.user_data["db_user"] = user
        return await func(update, context, *args, **kwargs)

    return wrapper


def admin_required(func):
    """Faqat admin uchun"""

    @wraps(func)
    async def wrapper(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        user = get_or_create_user(update)

        if not user.is_active:
            await update.message.reply_text("⛔ Sizning hisobingiz bloklangan.")
            return

        if not user.is_admin:
            await update.message.reply_text("⛔ Bu buyruq faqat admin uchun mavjud.")
            return

        context.user_data["db_user"] = user
        return await func(update, context, *args, **kwargs)

    return wrapper


def warehouse_required(func):
    """Faqat ombor hodimi yoki admin uchun"""

    @wraps(func)
    async def wrapper(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        user = get_or_create_user(update)

        if not user.is_active:
            await update.message.reply_text("⛔ Sizning hisobingiz bloklangan.")
            return

        if not user.is_warehouse:
            await update.message.reply_text(
                "⛔ Bu buyruq faqat ombor hodimlari uchun mavjud."
            )
            return

        context.user_data["db_user"] = user
        return await func(update, context, *args, **kwargs)

    return wrapper


def requester_required(func):
    """Faqat zakas qiluvchi uchun (aslida barcha foydalanuvchilar)"""

    @wraps(func)
    async def wrapper(
        update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
    ):
        user = get_or_create_user(update)

        if not user.is_active:
            await update.message.reply_text("⛔ Sizning hisobingiz bloklangan.")
            return

        context.user_data["db_user"] = user
        return await func(update, context, *args, **kwargs)

    return wrapper
