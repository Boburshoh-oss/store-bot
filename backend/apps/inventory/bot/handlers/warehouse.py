"""Ombor hodimi handlerlari"""

from telegram import Update
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ConversationHandler,
)

from apps.inventory.models import (
    Category,
    Product,
    Order,
    Transaction,
    OrderStatus,
    TransactionType,
    TelegramUser,
)
from apps.inventory.bot.decorators import warehouse_required, get_or_create_user
from apps.inventory.bot.keyboards import (
    get_main_menu_keyboard,
    get_cancel_keyboard,
    get_units_keyboard,
    get_categories_keyboard,
    get_products_keyboard,
    get_pending_orders_keyboard,
    get_order_actions_keyboard,
)
from apps.inventory.bot.utils import (
    parse_quantity,
    add_product_stock,
    remove_product_stock,
    format_order_info,
    format_transaction_history,
)
from apps.inventory.bot.notifications import notify_low_stock


# ============ Conversation States ============
(
    ADD_SELECT_CATEGORY,
    ADD_SELECT_PRODUCT,
    ADD_NEW_CATEGORY,
    ADD_NEW_PRODUCT,
    ADD_ENTER_QUANTITY,
    ADD_SELECT_UNIT,
    ADD_ENTER_MIN_QUANTITY,
) = range(7)

(
    GIVE_SELECT_ORDER,
    GIVE_CONFIRM,
) = range(10, 12)


# ============ Add Product Handlers ============


@warehouse_required
async def add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mahsulot qo'shishni boshlash"""
    await update.message.reply_text(
        "📁 Kategoriyani tanlang:", reply_markup=get_categories_keyboard("add_category")
    )
    return ADD_SELECT_CATEGORY


async def add_select_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kategoriya tanlash"""
    query = update.callback_query
    await query.answer()

    data = query.data.split(":")
    if data[1] == "new":
        await query.edit_message_text("📁 Yangi kategoriya nomini kiriting:")
        return ADD_NEW_CATEGORY

    category_id = int(data[1])
    context.user_data["category_id"] = category_id

    category = Category.objects.get(id=category_id)
    await query.edit_message_text(
        f"📁 Kategoriya: {category.name}\n\n📦 Mahsulotni tanlang yoki yangi qo'shing:",
        reply_markup=get_products_keyboard(category_id, "add_product"),
    )
    return ADD_SELECT_PRODUCT


async def add_new_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yangi kategoriya yaratish"""
    name = update.message.text.strip()

    if name == "❌ Bekor qilish":
        return await cancel_add(update, context)

    if len(name) < 2:
        await update.message.reply_text(
            "Kategoriya nomi kamida 2 ta belgidan iborat bo'lishi kerak."
        )
        return ADD_NEW_CATEGORY

    category, created = Category.objects.get_or_create(name=name)
    context.user_data["category_id"] = category.id

    if created:
        await update.message.reply_text(f"✅ '{name}' kategoriyasi yaratildi.")

    await update.message.reply_text(
        f"📦 Mahsulotni tanlang yoki yangi qo'shing:",
        reply_markup=get_products_keyboard(category.id, "add_product"),
    )
    return ADD_SELECT_PRODUCT


async def add_select_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mahsulot tanlash"""
    query = update.callback_query
    await query.answer()

    data = query.data.split(":")

    if query.data == "back_to_categories":
        await query.edit_message_text(
            "📁 Kategoriyani tanlang:",
            reply_markup=get_categories_keyboard("add_category"),
        )
        return ADD_SELECT_CATEGORY

    if query.data == "cancel":
        await query.edit_message_text("❌ Bekor qilindi.")
        return ConversationHandler.END

    if data[1] == "new":
        await query.edit_message_text("📦 Yangi mahsulot nomini kiriting:")
        return ADD_NEW_PRODUCT

    product_id = int(data[1])
    product = Product.objects.get(id=product_id)
    context.user_data["product_id"] = product_id
    context.user_data["is_new_product"] = False

    await query.edit_message_text(
        f"📦 Mahsulot: {product.name}\n"
        f"📊 Joriy miqdor: {product.quantity} {product.unit}\n\n"
        f"Qo'shiladigan miqdorni kiriting:",
        reply_markup=None,
    )
    await query.message.reply_text(
        "Miqdorni kiriting (masalan: 5 yoki 2.5):", reply_markup=get_cancel_keyboard()
    )
    return ADD_ENTER_QUANTITY


async def add_new_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yangi mahsulot nomi"""
    name = update.message.text.strip()

    if name == "❌ Bekor qilish":
        return await cancel_add(update, context)

    if len(name) < 2:
        await update.message.reply_text(
            "Mahsulot nomi kamida 2 ta belgidan iborat bo'lishi kerak."
        )
        return ADD_NEW_PRODUCT

    context.user_data["new_product_name"] = name
    context.user_data["is_new_product"] = True

    await update.message.reply_text(
        f"📦 Mahsulot: {name}\n\nMiqdorni kiriting (masalan: 5 yoki 2.5):",
        reply_markup=get_cancel_keyboard(),
    )
    return ADD_ENTER_QUANTITY


async def add_enter_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Miqdor kiritish"""
    text = update.message.text.strip()

    if text == "❌ Bekor qilish":
        return await cancel_add(update, context)

    success, quantity, error = parse_quantity(text)
    if not success:
        await update.message.reply_text(f"❌ {error}")
        return ADD_ENTER_QUANTITY

    context.user_data["quantity"] = quantity

    if context.user_data.get("is_new_product"):
        await update.message.reply_text(
            "📏 O'lchov birligini tanlang:", reply_markup=get_units_keyboard()
        )
        return ADD_SELECT_UNIT
    else:
        # Mavjud mahsulotga qo'shish
        return await complete_add(update, context)


async def add_select_unit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """O'lchov birligi tanlash"""
    text = update.message.text.strip()

    if text == "❌ Bekor qilish":
        return await cancel_add(update, context)

    valid_units = ["kg", "g", "l", "ml", "dona", "paket", "quti", "bo'lak"]
    if text not in valid_units:
        await update.message.reply_text(
            "Ro'yxatdan tanlang:", reply_markup=get_units_keyboard()
        )
        return ADD_SELECT_UNIT

    context.user_data["unit"] = text

    await update.message.reply_text(
        f"⚠️ Minimum miqdorni kiriting (ogohlantirish uchun).\n"
        f"0 kiritsangiz ogohlantirish bo'lmaydi:",
        reply_markup=get_cancel_keyboard(),
    )
    return ADD_ENTER_MIN_QUANTITY


async def add_enter_min_quantity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Minimum miqdor kiritish"""
    text = update.message.text.strip()

    if text == "❌ Bekor qilish":
        return await cancel_add(update, context)

    if text == "0":
        context.user_data["min_quantity"] = 0
    else:
        success, min_qty, error = parse_quantity(text)
        if not success:
            await update.message.reply_text(f"❌ {error}")
            return ADD_ENTER_MIN_QUANTITY
        context.user_data["min_quantity"] = min_qty

    return await complete_add(update, context)


async def complete_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Qo'shishni yakunlash"""
    user = get_or_create_user(update)
    quantity = context.user_data["quantity"]

    if context.user_data.get("is_new_product"):
        # Yangi mahsulot yaratish
        product = Product.objects.create(
            name=context.user_data["new_product_name"],
            category_id=context.user_data["category_id"],
            quantity=quantity,
            unit=context.user_data["unit"],
            min_quantity=context.user_data.get("min_quantity", 0),
        )

        # Tranzaksiya yaratish
        Transaction.objects.create(
            product=product,
            transaction_type=TransactionType.IN,
            quantity=quantity,
            performed_by=user,
            note="Yangi mahsulot",
        )

        message = (
            f"✅ Yangi mahsulot qo'shildi!\n\n"
            f"📦 {product.name}\n"
            f"📊 Miqdor: {product.quantity} {product.unit}\n"
            f"📁 Kategoriya: {product.category.name}"
        )
    else:
        # Mavjud mahsulotga qo'shish
        product = Product.objects.get(id=context.user_data["product_id"])
        old_quantity = product.quantity

        add_product_stock(product, quantity, user)

        message = (
            f"✅ Mahsulot qo'shildi!\n\n"
            f"📦 {product.name}\n"
            f"📊 Eski miqdor: {old_quantity} {product.unit}\n"
            f"➕ Qo'shildi: {quantity} {product.unit}\n"
            f"📊 Yangi miqdor: {product.quantity} {product.unit}"
        )

    await update.message.reply_text(
        message, reply_markup=get_main_menu_keyboard(user.role)
    )

    context.user_data.clear()
    context.user_data["db_user"] = user
    return ConversationHandler.END


async def cancel_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Qo'shishni bekor qilish"""
    user = get_or_create_user(update)
    context.user_data.clear()
    context.user_data["db_user"] = user

    await update.message.reply_text(
        "❌ Bekor qilindi.", reply_markup=get_main_menu_keyboard(user.role)
    )
    return ConversationHandler.END


# ============ Orders Handlers ============


@warehouse_required
async def orders_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kutilayotgan zakaslar"""
    pending_count = Order.objects.filter(status=OrderStatus.PENDING).count()

    text = f"📊 <b>Kutilayotgan zakaslar: {pending_count} ta</b>"

    await update.message.reply_text(
        text, parse_mode="HTML", reply_markup=get_pending_orders_keyboard()
    )


async def view_order_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Zakasni ko'rish"""
    query = update.callback_query
    await query.answer()

    if query.data == "no_orders":
        return

    if query.data == "back_to_orders":
        pending_count = Order.objects.filter(status=OrderStatus.PENDING).count()
        await query.edit_message_text(
            f"📊 <b>Kutilayotgan zakaslar: {pending_count} ta</b>",
            parse_mode="HTML",
            reply_markup=get_pending_orders_keyboard(),
        )
        return

    order_id = int(query.data.split(":")[1])

    try:
        order = Order.objects.select_related("product", "requester").get(id=order_id)
        text = format_order_info(order)

        await query.edit_message_text(
            text, parse_mode="HTML", reply_markup=get_order_actions_keyboard(order_id)
        )
    except Order.DoesNotExist:
        await query.edit_message_text("❌ Zakas topilmadi.")


async def complete_order_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Zakasni bajarish"""
    query = update.callback_query
    user = get_or_create_user(update)

    order_id = int(query.data.split(":")[1])

    try:
        order = Order.objects.select_related("product", "requester").get(
            id=order_id, status=OrderStatus.PENDING
        )

        product = order.product

        # Mahsulot yetarlimi tekshirish
        if product.quantity < order.quantity:
            await query.answer(
                f"❌ Yetarli mahsulot yo'q! Mavjud: {product.quantity} {product.unit}",
                show_alert=True,
            )
            return

        # Mahsulotni chiqarish
        success, transaction, error = remove_product_stock(
            product, order.quantity, user, order=order
        )

        if not success:
            await query.answer(f"❌ {error}", show_alert=True)
            return

        # Zakasni bajarish
        order.complete(user)

        await query.answer("✅ Zakas bajarildi!")

        # Zakas beruvchiga xabar
        try:
            await context.bot.send_message(
                chat_id=order.requester.telegram_id,
                text=f"✅ Sizning zakasngiz #{order.id} bajarildi!\n\n"
                f"📦 {product.name}\n"
                f"📊 Miqdor: {order.quantity} {product.unit}",
            )
        except Exception:
            pass  # Foydalanuvchi botni bloklagan bo'lishi mumkin

        # Kam qolgan bo'lsa ogohlantirish
        if product.is_low_stock:
            await notify_low_stock(context.bot, product)

        # Ro'yxatni yangilash
        pending_count = Order.objects.filter(status=OrderStatus.PENDING).count()
        await query.edit_message_text(
            f"✅ Zakas #{order_id} bajarildi!\n\n"
            f"📊 <b>Kutilayotgan zakaslar: {pending_count} ta</b>",
            parse_mode="HTML",
            reply_markup=get_pending_orders_keyboard(),
        )

    except Order.DoesNotExist:
        await query.answer(
            "❌ Zakas topilmadi yoki allaqachon bajarilgan.", show_alert=True
        )


async def cancel_order_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Zakasni bekor qilish"""
    query = update.callback_query

    order_id = int(query.data.split(":")[1])

    try:
        order = Order.objects.select_related("product", "requester").get(
            id=order_id, status=OrderStatus.PENDING
        )

        order.cancel()

        await query.answer("❌ Zakas bekor qilindi!")

        # Zakas beruvchiga xabar
        try:
            await context.bot.send_message(
                chat_id=order.requester.telegram_id,
                text=f"❌ Sizning zakasngiz #{order.id} bekor qilindi.\n\n"
                f"📦 {order.product.name}\n"
                f"📊 Miqdor: {order.quantity} {order.product.unit}",
            )
        except Exception:
            pass

        # Ro'yxatni yangilash
        pending_count = Order.objects.filter(status=OrderStatus.PENDING).count()
        await query.edit_message_text(
            f"❌ Zakas #{order_id} bekor qilindi!\n\n"
            f"📊 <b>Kutilayotgan zakaslar: {pending_count} ta</b>",
            parse_mode="HTML",
            reply_markup=get_pending_orders_keyboard(),
        )

    except Order.DoesNotExist:
        await query.answer("❌ Zakas topilmadi.", show_alert=True)


# ============ History Handler ============


@warehouse_required
async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kirim-chiqim tarixi"""
    transactions = Transaction.objects.select_related(
        "product", "performed_by"
    ).order_by("-created_at")[:30]

    text = format_transaction_history(transactions, limit=30)

    await update.message.reply_text(text, parse_mode="HTML")


# ============ Categories Handler ============


@warehouse_required
async def categories_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kategoriyalar ro'yxati"""
    categories = Category.objects.all()

    if not categories:
        text = "📁 Kategoriyalar yo'q.\n\nMahsulot qo'shish orqali kategoriya yarating: /add"
    else:
        lines = ["📁 <b>Kategoriyalar:</b>\n"]
        for cat in categories:
            product_count = cat.products.count()
            lines.append(f"• {cat.name} ({product_count} ta mahsulot)")
        text = "\n".join(lines)

    await update.message.reply_text(text, parse_mode="HTML")


# ============ Products Handler ============


@warehouse_required
async def products_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mahsulotlar boshqaruvi - list_command bilan bir xil"""
    from apps.inventory.bot.utils import format_product_list

    products = (
        Product.objects.all()
        .select_related("category")
        .order_by("category__name", "name")
    )
    text = format_product_list(products)

    await update.message.reply_text(text, parse_mode="HTML")


# ============ Give Order Handler (alias for orders) ============


@warehouse_required
async def give_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Zakas berish - orders bilan bir xil"""
    return await orders_command(update, context)


# ============ Create Handlers ============

add_product_handler = ConversationHandler(
    entry_points=[
        CommandHandler("add", add_start),
        MessageHandler(filters.Regex(r"^➕ Mahsulot qo'shish$"), add_start),
    ],
    states={
        ADD_SELECT_CATEGORY: [
            CallbackQueryHandler(add_select_category, pattern=r"^add_category:"),
            CallbackQueryHandler(cancel_add, pattern=r"^cancel$"),
        ],
        ADD_NEW_CATEGORY: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, add_new_category),
        ],
        ADD_SELECT_PRODUCT: [
            CallbackQueryHandler(
                add_select_product, pattern=r"^(add_product:|back_to_categories|cancel)"
            ),
        ],
        ADD_NEW_PRODUCT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, add_new_product),
        ],
        ADD_ENTER_QUANTITY: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, add_enter_quantity),
        ],
        ADD_SELECT_UNIT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, add_select_unit),
        ],
        ADD_ENTER_MIN_QUANTITY: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, add_enter_min_quantity),
        ],
    },
    fallbacks=[
        CommandHandler("cancel", cancel_add),
        MessageHandler(filters.Regex(r"^❌ Bekor qilish$"), cancel_add),
    ],
)

# Orders handlers
orders_handler = CommandHandler("orders", orders_command)
give_order_handler = CommandHandler("give", give_command)
history_handler = CommandHandler("history", history_command)
categories_handler = CommandHandler("categories", categories_command)
products_handler = CommandHandler("products", products_command)
