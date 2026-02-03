#!/usr/bin/env python
"""Telegram botni ishga tushirish skripti"""
import os
import sys
import logging

# Django sozlamalarini yuklash
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
# Django ORM ni async kontekstda ishlashga ruxsat berish
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

import django

django.setup()

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from django.conf import settings

# Bot handlerlarini import qilish
from apps.inventory.bot.handlers import (
    # Common
    start_handler,
    help_handler,
    list_handler,
    cancel_handler,
    # Warehouse
    add_product_handler,
    orders_handler,
    give_order_handler,
    history_handler,
    categories_handler,
    products_handler,
    # Requester
    order_handler,
    my_orders_handler,
    # Admin
    users_handler,
)
from apps.inventory.bot.handlers.common import cancel_callback
from apps.inventory.bot.handlers.warehouse import (
    view_order_callback,
    complete_order_callback,
    cancel_order_callback,
)
from apps.inventory.bot.handlers.admin import (
    users_page_callback,
    user_detail_callback,
    set_role_callback,
    block_user_callback,
    unblock_user_callback,
)
from apps.inventory.bot.handlers.requester import my_order_callback
from apps.inventory.bot.keyboards import get_main_menu_keyboard
from apps.inventory.bot.decorators import get_or_create_user

# Logging sozlamalari
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# ============ Menu Button Handlers ============


async def menu_list_handler(update: Update, context):
    """Ro'yxat tugmasi"""
    from apps.inventory.bot.handlers.common import list_command

    return await list_command(update, context)


async def menu_my_orders_handler(update: Update, context):
    """Mening zakaslarim tugmasi"""
    from apps.inventory.bot.handlers.requester import my_orders_command

    return await my_orders_command(update, context)


async def menu_orders_handler(update: Update, context):
    """Kutilayotgan zakaslar tugmasi"""
    from apps.inventory.bot.handlers.warehouse import orders_command

    return await orders_command(update, context)


async def menu_history_handler(update: Update, context):
    """Tarix tugmasi"""
    from apps.inventory.bot.handlers.warehouse import history_command

    return await history_command(update, context)


async def menu_categories_handler(update: Update, context):
    """Kategoriyalar tugmasi"""
    from apps.inventory.bot.handlers.warehouse import categories_command

    return await categories_command(update, context)


async def menu_products_handler(update: Update, context):
    """Mahsulotlar tugmasi"""
    from apps.inventory.bot.handlers.warehouse import products_command

    return await products_command(update, context)


async def menu_users_handler(update: Update, context):
    """Foydalanuvchilar tugmasi"""
    from apps.inventory.bot.handlers.admin import users_command

    return await users_command(update, context)


async def unknown_command(update: Update, context):
    """Noma'lum buyruq"""
    user = get_or_create_user(update)
    await update.message.reply_text(
        "❓ Noma'lum buyruq.\n\nYordam uchun: /help",
        reply_markup=get_main_menu_keyboard(user.role),
    )


def main():
    """Botni ishga tushirish"""
    # Token tekshirish
    token = getattr(settings, "TELEGRAM_BOT_TOKEN", None) or os.getenv(
        "TELEGRAM_BOT_TOKEN"
    )

    if not token:
        logger.error("TELEGRAM_BOT_TOKEN topilmadi! .env faylini tekshiring.")
        sys.exit(1)

    # Application yaratish
    application = Application.builder().token(token).build()

    # ============ Handlers qo'shish ============

    # Conversation handlers (birinchi navbatda)
    application.add_handler(add_product_handler)  # /add
    application.add_handler(order_handler)  # /order

    # Command handlers
    application.add_handler(start_handler)  # /start
    application.add_handler(help_handler)  # /help
    application.add_handler(list_handler)  # /list
    application.add_handler(cancel_handler)  # /cancel
    application.add_handler(orders_handler)  # /orders
    application.add_handler(give_order_handler)  # /give
    application.add_handler(history_handler)  # /history
    application.add_handler(categories_handler)  # /categories
    application.add_handler(products_handler)  # /products
    application.add_handler(my_orders_handler)  # /myorders
    application.add_handler(users_handler)  # /users

    # Menu button handlers
    application.add_handler(
        MessageHandler(filters.Regex(r"^📋 Ro'yxat$"), menu_list_handler)
    )
    application.add_handler(
        MessageHandler(filters.Regex(r"^📝 Mening zakaslarim$"), menu_my_orders_handler)
    )
    application.add_handler(
        MessageHandler(
            filters.Regex(r"^📊 Kutilayotgan zakaslar$"), menu_orders_handler
        )
    )
    application.add_handler(
        MessageHandler(filters.Regex(r"^📤 Zakas berish$"), menu_orders_handler)
    )
    application.add_handler(
        MessageHandler(filters.Regex(r"^📜 Tarix$"), menu_history_handler)
    )
    application.add_handler(
        MessageHandler(filters.Regex(r"^📁 Kategoriyalar$"), menu_categories_handler)
    )
    application.add_handler(
        MessageHandler(filters.Regex(r"^📦 Mahsulotlar$"), menu_products_handler)
    )
    application.add_handler(
        MessageHandler(filters.Regex(r"^👥 Foydalanuvchilar$"), menu_users_handler)
    )

    # Callback handlers
    # Orders
    application.add_handler(
        CallbackQueryHandler(view_order_callback, pattern=r"^view_order:")
    )
    application.add_handler(
        CallbackQueryHandler(complete_order_callback, pattern=r"^complete_order:")
    )
    application.add_handler(
        CallbackQueryHandler(cancel_order_callback, pattern=r"^cancel_order:")
    )
    application.add_handler(
        CallbackQueryHandler(view_order_callback, pattern=r"^back_to_orders$")
    )

    # Users
    application.add_handler(
        CallbackQueryHandler(users_page_callback, pattern=r"^users_page:")
    )
    application.add_handler(
        CallbackQueryHandler(user_detail_callback, pattern=r"^user:")
    )
    application.add_handler(
        CallbackQueryHandler(user_detail_callback, pattern=r"^back_to_users$")
    )
    application.add_handler(
        CallbackQueryHandler(set_role_callback, pattern=r"^set_role:")
    )
    application.add_handler(
        CallbackQueryHandler(block_user_callback, pattern=r"^block_user:")
    )
    application.add_handler(
        CallbackQueryHandler(unblock_user_callback, pattern=r"^unblock_user:")
    )

    # My orders
    application.add_handler(
        CallbackQueryHandler(my_order_callback, pattern=r"^my_order:")
    )

    # Cancel callback
    application.add_handler(CallbackQueryHandler(cancel_callback, pattern=r"^cancel$"))
    application.add_handler(
        CallbackQueryHandler(
            lambda u, c: u.callback_query.answer(), pattern=r"^no_orders$"
        )
    )

    # Unknown commands
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))

    # ============ Botni ishga tushirish ============
    logger.info("Bot ishga tushirildi...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
