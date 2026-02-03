"""
Telegram bot handlers for warehouse management
"""
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)
from apps.products.models import Product, Category
from apps.inventory.models import Stock, Warehouse


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    keyboard = [
        [InlineKeyboardButton("📦 Mahsulotlar / Products", callback_data='products')],
        [InlineKeyboardButton("📊 Qoldiqlar / Stock", callback_data='stock')],
        [InlineKeyboardButton("⚠️ Kam qoldiqlar / Low Stock", callback_data='low_stock')],
        [InlineKeyboardButton("🏢 Omborlar / Warehouses", callback_data='warehouses')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🏪 Ombor boshqaruv tizimiga xush kelibsiz!\n"
        "Welcome to Warehouse Management System!\n\n"
        "Quyidagi tugmalardan birini tanlang:",
        reply_markup=reply_markup
    )


async def products_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all products"""
    query = update.callback_query
    await query.answer()
    
    products = Product.objects.filter(is_active=True)[:10]
    
    if not products:
        await query.edit_message_text("Mahsulotlar topilmadi / No products found")
        return
    
    message = "📦 <b>Mahsulotlar ro'yxati / Products List:</b>\n\n"
    for product in products:
        message += f"• <b>{product.name}</b>\n"
        message += f"  Kategoriya: {product.category.name}\n"
        message += f"  Narxi: {product.price} so'm\n"
        if product.barcode:
            message += f"  Shtrix-kod: {product.barcode}\n"
        message += "\n"
    
    keyboard = [[InlineKeyboardButton("🔙 Orqaga / Back", callback_data='start')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')


async def stock_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show stock information"""
    query = update.callback_query
    await query.answer()
    
    stocks = Stock.objects.select_related('product', 'warehouse').all()[:10]
    
    if not stocks:
        await query.edit_message_text("Qoldiqlar topilmadi / No stock found")
        return
    
    message = "📊 <b>Qoldiqlar ro'yxati / Stock List:</b>\n\n"
    for stock in stocks:
        message += f"• <b>{stock.product.name}</b>\n"
        message += f"  Ombor: {stock.warehouse.name}\n"
        message += f"  Miqdor: {stock.quantity}\n"
        message += f"  Status: {'✅ Yetarli' if not stock.is_low_stock else '⚠️ Kam'}\n"
        message += "\n"
    
    keyboard = [[InlineKeyboardButton("🔙 Orqaga / Back", callback_data='start')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')


async def low_stock_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show low stock items"""
    query = update.callback_query
    await query.answer()
    
    from django.db.models import F
    low_stocks = Stock.objects.select_related('product', 'warehouse').filter(
        quantity__lte=F('min_quantity')
    )[:10]
    
    if not low_stocks:
        message = "✅ Kam qoldiqlar yo'q / No low stock items"
    else:
        message = "⚠️ <b>Kam qoldiqlar / Low Stock Items:</b>\n\n"
        for stock in low_stocks:
            message += f"• <b>{stock.product.name}</b>\n"
            message += f"  Ombor: {stock.warehouse.name}\n"
            message += f"  Hozirgi miqdor: {stock.quantity}\n"
            message += f"  Minimal miqdor: {stock.min_quantity}\n"
            message += "\n"
    
    keyboard = [[InlineKeyboardButton("🔙 Orqaga / Back", callback_data='start')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')


async def warehouses_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all warehouses"""
    query = update.callback_query
    await query.answer()
    
    from django.db.models import Count
    warehouses = Warehouse.objects.annotate(stock_count=Count('stocks')).all()
    
    if not warehouses:
        await query.edit_message_text("Omborlar topilmadi / No warehouses found")
        return
    
    message = "🏢 <b>Omborlar ro'yxati / Warehouses List:</b>\n\n"
    for warehouse in warehouses:
        message += f"• <b>{warehouse.name}</b>\n"
        if warehouse.location:
            message += f"  Manzil: {warehouse.location}\n"
        message += f"  Mahsulotlar soni: {warehouse.stock_count}\n"
        message += "\n"
    
    keyboard = [[InlineKeyboardButton("🔙 Orqaga / Back", callback_data='start')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    
    if query.data == 'start':
        keyboard = [
            [InlineKeyboardButton("📦 Mahsulotlar / Products", callback_data='products')],
            [InlineKeyboardButton("📊 Qoldiqlar / Stock", callback_data='stock')],
            [InlineKeyboardButton("⚠️ Kam qoldiqlar / Low Stock", callback_data='low_stock')],
            [InlineKeyboardButton("🏢 Omborlar / Warehouses", callback_data='warehouses')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🏪 Ombor boshqaruv tizimiga xush kelibsiz!\n"
            "Welcome to Warehouse Management System!\n\n"
            "Quyidagi tugmalardan birini tanlang:",
            reply_markup=reply_markup
        )
    elif query.data == 'products':
        await products_handler(update, context)
    elif query.data == 'stock':
        await stock_handler(update, context)
    elif query.data == 'low_stock':
        await low_stock_handler(update, context)
    elif query.data == 'warehouses':
        await warehouses_handler(update, context)


def setup_bot():
    """Setup and configure the bot"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
    
    application = Application.builder().token(token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    return application


def run_bot():
    """Run the bot"""
    application = setup_bot()
    application.run_polling(allowed_updates=Update.ALL_TYPES)
