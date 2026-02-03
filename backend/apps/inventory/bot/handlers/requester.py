"""Zakas qiluvchi handlerlari"""

from telegram import Update
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ConversationHandler,
)

from apps.inventory.models import Category, Product, Order, OrderStatus, TelegramUser
from apps.inventory.bot.decorators import requester_required, get_or_create_user
from apps.inventory.bot.keyboards import (
    get_main_menu_keyboard,
    get_cancel_keyboard,
    get_categories_keyboard,
    get_products_keyboard,
    get_my_orders_keyboard,
)
from apps.inventory.bot.utils import parse_quantity, format_order_info
from apps.inventory.bot.notifications import notify_new_order


# ============ Conversation States ============
(
    ORDER_SELECT_CATEGORY,
    ORDER_SELECT_PRODUCT,
    ORDER_ENTER_QUANTITY,
    ORDER_ENTER_NOTE,
) = range(20, 24)


# ============ Order Handlers ============


@requester_required
async def order_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Zakas qilishni boshlash"""
    categories = Category.objects.all()

    if not categories.exists():
        await update.message.reply_text(
            "📭 Hozircha kategoriyalar yo'q. Ombor hodimidan mahsulot qo'shishni so'rang."
        )
        return ConversationHandler.END

    await update.message.reply_text(
        "📦 <b>Yangi zakas</b>\n\n📁 Kategoriyani tanlang:",
        parse_mode="HTML",
        reply_markup=get_categories_keyboard("order_category"),
    )
    return ORDER_SELECT_CATEGORY


async def order_select_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kategoriya tanlash"""
    query = update.callback_query
    await query.answer()

    if query.data == "cancel":
        await query.edit_message_text("❌ Zakas bekor qilindi.")
        return ConversationHandler.END

    category_id = int(query.data.split(":")[1])
    context.user_data["order_category_id"] = category_id

    # Mahsulotlar borligini tekshirish
    products = Product.objects.filter(category_id=category_id, quantity__gt=0)

    if not products.exists():
        await query.answer("Bu kategoriyada mavjud mahsulotlar yo'q.", show_alert=True)
        return ORDER_SELECT_CATEGORY

    category = Category.objects.get(id=category_id)
    await query.edit_message_text(
        f"📁 Kategoriya: {category.name}\n\n📦 Mahsulotni tanlang:",
        reply_markup=get_products_keyboard(category_id, "order_product"),
    )
    return ORDER_SELECT_PRODUCT


async def order_select_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mahsulot tanlash"""
    query = update.callback_query
    await query.answer()

    if query.data == "cancel":
        await query.edit_message_text("❌ Zakas bekor qilindi.")
        return ConversationHandler.END

    if query.data == "back_to_categories":
        await query.edit_message_text(
            "📁 Kategoriyani tanlang:",
            reply_markup=get_categories_keyboard("order_category"),
        )
        return ORDER_SELECT_CATEGORY

    product_id = int(query.data.split(":")[1])
    product = Product.objects.get(id=product_id)

    if product.quantity <= 0:
        await query.answer("Bu mahsulot tugagan!", show_alert=True)
        return ORDER_SELECT_PRODUCT

    context.user_data["order_product_id"] = product_id

    await query.edit_message_text(
        f"📦 <b>{product.name}</b>\n"
        f"📊 Mavjud: {product.quantity} {product.unit}\n\n"
        f"Qancha miqdor kerak?",
        parse_mode="HTML",
    )
    await query.message.reply_text(
        f"Miqdorni kiriting ({product.unit}):", reply_markup=get_cancel_keyboard()
    )
    return ORDER_ENTER_QUANTITY


async def order_enter_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Miqdor kiritish"""
    text = update.message.text.strip()

    if text == "❌ Bekor qilish":
        return await cancel_order(update, context)

    success, quantity, error = parse_quantity(text)
    if not success:
        await update.message.reply_text(f"❌ {error}")
        return ORDER_ENTER_QUANTITY

    product = Product.objects.get(id=context.user_data["order_product_id"])

    if quantity > product.quantity:
        await update.message.reply_text(
            f"❌ Yetarli mahsulot yo'q.\n"
            f"📊 Mavjud: {product.quantity} {product.unit}\n\n"
            f"Boshqa miqdor kiriting:"
        )
        return ORDER_ENTER_QUANTITY

    context.user_data["order_quantity"] = quantity

    await update.message.reply_text(
        f"📝 Izoh qo'shmoqchimisiz? (ixtiyoriy)\n\n"
        f"Izoh yozing yoki 'Yo'q' deb yuboring:",
        reply_markup=get_cancel_keyboard(),
    )
    return ORDER_ENTER_NOTE


async def order_enter_note(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Izoh kiritish va zakasni yaratish"""
    text = update.message.text.strip()

    if text == "❌ Bekor qilish":
        return await cancel_order(update, context)

    user = get_or_create_user(update)
    product = Product.objects.get(id=context.user_data["order_product_id"])
    quantity = context.user_data["order_quantity"]
    note = None if text.lower() in ["yo'q", "yoq", "-", ""] else text

    # Zakasni yaratish
    order = Order.objects.create(
        requester=user,
        product=product,
        quantity=quantity,
        note=note,
        status=OrderStatus.PENDING,
    )

    await update.message.reply_text(
        f"✅ <b>Zakas qabul qilindi!</b>\n\n"
        f"📋 Zakas raqami: #{order.id}\n"
        f"📦 Mahsulot: {product.name}\n"
        f"📊 Miqdor: {quantity} {product.unit}\n"
        f"⏳ Holat: Kutilmoqda\n\n"
        f"Ombor hodimi tez orada javob beradi.",
        parse_mode="HTML",
        reply_markup=get_main_menu_keyboard(user.role),
    )

    # Ombor hodimlariga xabar
    await notify_new_order(update.get_bot(), order, user)

    context.user_data.clear()
    context.user_data["db_user"] = user
    return ConversationHandler.END


async def cancel_order(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Zakasni bekor qilish"""
    user = get_or_create_user(update)
    context.user_data.clear()
    context.user_data["db_user"] = user

    await update.message.reply_text(
        "❌ Zakas bekor qilindi.", reply_markup=get_main_menu_keyboard(user.role)
    )
    return ConversationHandler.END


# ============ My Orders Handler ============


@requester_required
async def my_orders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mening zakaslarim"""
    user: TelegramUser = context.user_data["db_user"]

    orders = Order.objects.filter(requester=user).select_related("product")[:10]

    if not orders:
        await update.message.reply_text(
            "📭 Sizda hali zakaslar yo'q.\n\n" "Zakas qilish uchun: /order"
        )
        return

    lines = ["📝 <b>Mening zakaslarim:</b>\n"]

    for order in orders:
        status_emoji = (
            "⏳"
            if order.status == OrderStatus.PENDING
            else "✅" if order.status == OrderStatus.COMPLETED else "❌"
        )
        lines.append(
            f"{status_emoji} #{order.id} | {order.product.name} - "
            f"{order.quantity} {order.product.unit} | "
            f"{order.created_at.strftime('%d.%m.%Y')}"
        )

    await update.message.reply_text("\n".join(lines), parse_mode="HTML")


async def my_order_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Zakasni batafsil ko'rish"""
    query = update.callback_query
    await query.answer()

    if query.data == "no_orders":
        return

    order_id = int(query.data.split(":")[1])

    try:
        order = Order.objects.select_related(
            "product", "requester", "fulfilled_by"
        ).get(id=order_id)
        text = format_order_info(order)
        await query.edit_message_text(text, parse_mode="HTML")
    except Order.DoesNotExist:
        await query.edit_message_text("❌ Zakas topilmadi.")


# ============ Create Handlers ============

order_handler = ConversationHandler(
    entry_points=[
        CommandHandler("order", order_start),
        MessageHandler(filters.Regex(r"^📦 Zakas qilish$"), order_start),
    ],
    states={
        ORDER_SELECT_CATEGORY: [
            CallbackQueryHandler(
                order_select_category, pattern=r"^(order_category:|cancel)"
            ),
        ],
        ORDER_SELECT_PRODUCT: [
            CallbackQueryHandler(
                order_select_product,
                pattern=r"^(order_product:|back_to_categories|cancel)",
            ),
        ],
        ORDER_ENTER_QUANTITY: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, order_enter_quantity),
        ],
        ORDER_ENTER_NOTE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, order_enter_note),
        ],
    },
    fallbacks=[
        CommandHandler("cancel", cancel_order),
        MessageHandler(filters.Regex(r"^❌ Bekor qilish$"), cancel_order),
    ],
)

my_orders_handler = CommandHandler("myorders", my_orders_command)
