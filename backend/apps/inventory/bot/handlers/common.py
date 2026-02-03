"""Umumiy handlerlar - barcha foydalanuvchilar uchun"""

from telegram import Update
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
)

from apps.inventory.models import TelegramUser, UserRole, Product
from apps.inventory.bot.decorators import authenticated, get_or_create_user
from apps.inventory.bot.keyboards import get_main_menu_keyboard
from apps.inventory.bot.utils import format_product_list


@authenticated
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Botni ishga tushirish"""
    user: TelegramUser = context.user_data["db_user"]

    # Birinchi foydalanuvchini admin qilish
    if TelegramUser.objects.count() == 1 and user.role == UserRole.REQUESTER:
        user.role = UserRole.ADMIN
        user.save()
        context.user_data["db_user"] = user

    role_text = user.get_role_display()

    welcome_text = f"""
🏠 <b>Uy ombor botiga xush kelibsiz!</b>

👤 Ism: {user.full_name}
🎭 Rol: {role_text}

📋 Asosiy buyruqlar:
/list - Mahsulotlar ro'yxati
/order - Zakas qilish
/myorders - Mening zakaslarim
/help - Yordam
"""

    if user.is_warehouse:
        welcome_text += """
📦 <b>Ombor hodimi buyruqlari:</b>
/add - Mahsulot qo'shish
/orders - Kutilayotgan zakaslar
/give - Zakas bajarish
/history - Kirim-chiqim tarixi
/categories - Kategoriyalar
/products - Mahsulotlar
"""

    if user.is_admin:
        welcome_text += """
👑 <b>Admin buyruqlari:</b>
/users - Foydalanuvchilar
"""

    await update.message.reply_text(
        welcome_text, parse_mode="HTML", reply_markup=get_main_menu_keyboard(user.role)
    )


@authenticated
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yordam"""
    user: TelegramUser = context.user_data["db_user"]

    help_text = """
📚 <b>Yordam</b>

<b>Umumiy buyruqlar:</b>
/start - Botni qayta ishga tushirish
/list - Ombordagi mahsulotlar ro'yxati
/order - Yangi zakas qilish
/myorders - Mening zakaslarim

/help - Ushbu yordam
/cancel - Joriy amalni bekor qilish
"""

    if user.is_warehouse:
        help_text += """
<b>Ombor hodimi buyruqlari:</b>
/add - Omborga mahsulot qo'shish
/orders - Kutilayotgan zakaslar ro'yxati
/give - Zakas bo'yicha mahsulot berish
/history - Kirim-chiqim tarixi
/categories - Kategoriyalarni boshqarish
/products - Mahsulotlarni boshqarish
"""

    if user.is_admin:
        help_text += """
<b>Admin buyruqlari:</b>
/users - Foydalanuvchilarni boshqarish
"""

    await update.message.reply_text(help_text, parse_mode="HTML")


@authenticated
async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mahsulotlar ro'yxati"""
    products = (
        Product.objects.all()
        .select_related("category")
        .order_by("category__name", "name")
    )
    text = format_product_list(products)

    await update.message.reply_text(text, parse_mode="HTML")


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Amalni bekor qilish"""
    user = get_or_create_user(update)

    # Context ma'lumotlarini tozalash
    context.user_data.clear()
    context.user_data["db_user"] = user

    await update.message.reply_text(
        "❌ Amal bekor qilindi.", reply_markup=get_main_menu_keyboard(user.role)
    )
    return ConversationHandler.END


async def cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Callback orqali bekor qilish"""
    query = update.callback_query
    await query.answer()

    user = get_or_create_user(update)
    context.user_data.clear()
    context.user_data["db_user"] = user

    await query.edit_message_text("❌ Bekor qilindi.")
    return ConversationHandler.END


# Handler yaratish
start_handler = CommandHandler("start", start_command)
help_handler = CommandHandler("help", help_command)
list_handler = CommandHandler("list", list_command)
cancel_handler = CommandHandler("cancel", cancel_command)
