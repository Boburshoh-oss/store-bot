"""Telegram klaviaturalari"""

from telegram import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove,
)

from apps.inventory.models import Category, Product, Order, OrderStatus, UserRole


# ============ Reply Keyboards ============


def get_main_menu_keyboard(user_role: str) -> ReplyKeyboardMarkup:
    """Asosiy menyu klaviaturasi (rolga qarab)"""

    # Barcha foydalanuvchilar uchun
    common_buttons = [
        ["📋 Ro'yxat", "📦 Zakas qilish"],
        ["📝 Mening zakaslarim"],
    ]

    # Ombor hodimi uchun qo'shimcha tugmalar
    if user_role in [UserRole.ADMIN, UserRole.WAREHOUSE]:
        warehouse_buttons = [
            ["➕ Mahsulot qo'shish", "📤 Zakas berish"],
            ["📊 Kutilayotgan zakaslar", "📜 Tarix"],
            ["📁 Kategoriyalar", "📦 Mahsulotlar"],
        ]
        common_buttons = warehouse_buttons + common_buttons

    # Admin uchun qo'shimcha tugmalar
    if user_role == UserRole.ADMIN:
        admin_buttons = [
            ["👥 Foydalanuvchilar"],
        ]
        common_buttons = admin_buttons + common_buttons

    return ReplyKeyboardMarkup(common_buttons, resize_keyboard=True)


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Bekor qilish tugmasi"""
    return ReplyKeyboardMarkup([["❌ Bekor qilish"]], resize_keyboard=True)


def get_units_keyboard() -> ReplyKeyboardMarkup:
    """O'lchov birliklari"""
    units = [
        ["kg", "g", "l", "ml"],
        ["dona", "paket", "quti", "bo'lak"],
        ["❌ Bekor qilish"],
    ]
    return ReplyKeyboardMarkup(units, resize_keyboard=True)


# ============ Inline Keyboards ============


def get_categories_keyboard(action_prefix: str = "category") -> InlineKeyboardMarkup:
    """Kategoriyalar inline klaviaturasi"""
    categories = Category.objects.all()
    buttons = []

    for category in categories:
        buttons.append(
            [
                InlineKeyboardButton(
                    category.name, callback_data=f"{action_prefix}:{category.id}"
                )
            ]
        )

    if action_prefix in ["add_category", "select_category"]:
        buttons.append(
            [
                InlineKeyboardButton(
                    "➕ Yangi kategoriya", callback_data=f"{action_prefix}:new"
                )
            ]
        )

    buttons.append([InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel")])

    return InlineKeyboardMarkup(buttons)


def get_products_keyboard(
    category_id: int, action_prefix: str = "product"
) -> InlineKeyboardMarkup:
    """Mahsulotlar inline klaviaturasi"""
    products = Product.objects.filter(category_id=category_id)
    buttons = []

    for product in products:
        stock_info = f" ({product.quantity} {product.unit})"
        buttons.append(
            [
                InlineKeyboardButton(
                    f"{product.name}{stock_info}",
                    callback_data=f"{action_prefix}:{product.id}",
                )
            ]
        )

    if action_prefix in ["add_product", "select_product"]:
        buttons.append(
            [
                InlineKeyboardButton(
                    "➕ Yangi mahsulot", callback_data=f"{action_prefix}:new"
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_categories"),
            InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel"),
        ]
    )

    return InlineKeyboardMarkup(buttons)


def get_pending_orders_keyboard() -> InlineKeyboardMarkup:
    """Kutilayotgan zakaslar"""
    orders = Order.objects.filter(status=OrderStatus.PENDING).select_related(
        "product", "requester"
    )
    buttons = []

    for order in orders[:20]:  # Maksimum 20 ta
        text = (
            f"#{order.id} {order.product.name} - {order.quantity} {order.product.unit}"
        )
        buttons.append(
            [InlineKeyboardButton(text, callback_data=f"view_order:{order.id}")]
        )

    if not buttons:
        buttons.append(
            [InlineKeyboardButton("📭 Zakaslar yo'q", callback_data="no_orders")]
        )

    buttons.append([InlineKeyboardButton("❌ Yopish", callback_data="cancel")])

    return InlineKeyboardMarkup(buttons)


def get_order_actions_keyboard(order_id: int) -> InlineKeyboardMarkup:
    """Zakas harakatlari"""
    buttons = [
        [
            InlineKeyboardButton(
                "✅ Bajarish", callback_data=f"complete_order:{order_id}"
            ),
            InlineKeyboardButton(
                "❌ Bekor qilish", callback_data=f"cancel_order:{order_id}"
            ),
        ],
        [InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_orders")],
    ]
    return InlineKeyboardMarkup(buttons)


def get_users_keyboard(page: int = 0, per_page: int = 10) -> InlineKeyboardMarkup:
    """Foydalanuvchilar ro'yxati"""
    from apps.inventory.models import TelegramUser

    users = TelegramUser.objects.all()[page * per_page : (page + 1) * per_page]
    total = TelegramUser.objects.count()
    buttons = []

    for user in users:
        role_emoji = (
            "👑"
            if user.role == UserRole.ADMIN
            else "📦" if user.role == UserRole.WAREHOUSE else "👤"
        )
        status = "🟢" if user.is_active else "🔴"
        buttons.append(
            [
                InlineKeyboardButton(
                    f"{status} {role_emoji} {user.full_name}",
                    callback_data=f"user:{user.id}",
                )
            ]
        )

    # Pagination
    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton("⬅️ Oldingi", callback_data=f"users_page:{page-1}")
        )
    if (page + 1) * per_page < total:
        nav_buttons.append(
            InlineKeyboardButton("Keyingi ➡️", callback_data=f"users_page:{page+1}")
        )
    if nav_buttons:
        buttons.append(nav_buttons)

    buttons.append([InlineKeyboardButton("❌ Yopish", callback_data="cancel")])

    return InlineKeyboardMarkup(buttons)


def get_user_actions_keyboard(
    user_id: int, current_role: str, is_active: bool
) -> InlineKeyboardMarkup:
    """Foydalanuvchi harakatlari"""
    buttons = []

    # Rol o'zgartirish
    role_buttons = []
    if current_role != UserRole.ADMIN:
        role_buttons.append(
            InlineKeyboardButton("👑 Admin", callback_data=f"set_role:{user_id}:admin")
        )
    if current_role != UserRole.WAREHOUSE:
        role_buttons.append(
            InlineKeyboardButton(
                "📦 Ombor", callback_data=f"set_role:{user_id}:warehouse"
            )
        )
    if current_role != UserRole.REQUESTER:
        role_buttons.append(
            InlineKeyboardButton(
                "👤 Zakas", callback_data=f"set_role:{user_id}:requester"
            )
        )

    if role_buttons:
        buttons.append(role_buttons)

    # Bloklash/Aktivlashtirish
    if is_active:
        buttons.append(
            [InlineKeyboardButton("🔴 Bloklash", callback_data=f"block_user:{user_id}")]
        )
    else:
        buttons.append(
            [
                InlineKeyboardButton(
                    "🟢 Aktivlashtirish", callback_data=f"unblock_user:{user_id}"
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton("🔙 Orqaga", callback_data="back_to_users"),
            InlineKeyboardButton("❌ Yopish", callback_data="cancel"),
        ]
    )

    return InlineKeyboardMarkup(buttons)


def get_my_orders_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Mening zakaslarim"""
    from apps.inventory.models import TelegramUser

    orders = Order.objects.filter(requester_id=user_id).select_related("product")[:20]
    buttons = []

    for order in orders:
        status_emoji = (
            "⏳"
            if order.status == OrderStatus.PENDING
            else "✅" if order.status == OrderStatus.COMPLETED else "❌"
        )
        text = f"{status_emoji} #{order.id} {order.product.name} - {order.quantity} {order.product.unit}"
        buttons.append(
            [InlineKeyboardButton(text, callback_data=f"my_order:{order.id}")]
        )

    if not buttons:
        buttons.append(
            [InlineKeyboardButton("📭 Zakaslar yo'q", callback_data="no_orders")]
        )

    buttons.append([InlineKeyboardButton("❌ Yopish", callback_data="cancel")])

    return InlineKeyboardMarkup(buttons)


def get_confirm_keyboard(action: str, item_id: int) -> InlineKeyboardMarkup:
    """Tasdiqlash klaviaturasi"""
    buttons = [
        [
            InlineKeyboardButton("✅ Ha", callback_data=f"confirm_{action}:{item_id}"),
            InlineKeyboardButton("❌ Yo'q", callback_data="cancel"),
        ]
    ]
    return InlineKeyboardMarkup(buttons)
