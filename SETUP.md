# Ombor Boshqaruv Tizimi / Warehouse Management System

Django asosidagi ombor boshqaruv tizimi Telegram bot integratsiyasi bilan.
A Django-based warehouse management system with Telegram bot integration.

## Xususiyatlar / Features

### Backend (Django REST API)
- ✅ Mahsulotlar boshqaruvi / Product management
- ✅ Kategoriyalar / Categories
- ✅ Ombor qoldiqlari / Inventory tracking
- ✅ Mahsulot harakati / Stock movements (IN/OUT/TRANSFER)
- ✅ Kam qoldiq ogohlantirishi / Low stock alerts
- ✅ REST API endpoints

### Telegram Bot
- ✅ Mahsulotlar ro'yxatini ko'rish / View products list
- ✅ Qoldiqlarni tekshirish / Check stock levels
- ✅ Kam qoldiqlar haqida xabar olish / Get low stock alerts
- ✅ Omborlar ro'yxati / List warehouses

## O'rnatish / Installation

### 1. Talablar / Requirements
```bash
pip install -r requirements.txt
```

### 2. Environment sozlamalari / Environment setup
`.env` faylini yarating va quyidagilarni to'ldiring:
Create a `.env` file and fill in:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DJANGO_SETTINGS_MODULE=config.settings.development

# Database
DB_NAME=store_bot
DB_USERNAME=postgres
DB_PASSWORD=postgres
DB_HOSTNAME=localhost
DB_PORT=5432

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
```

### 3. Database migratsiyalari / Database migrations
```bash
cd backend
python manage.py migrate
```

### 4. Superuser yaratish / Create superuser
```bash
python manage.py createsuperuser
```

### 5. Django serverni ishga tushirish / Start Django server
```bash
python manage.py runserver
```

### 6. Telegram botni ishga tushirish / Start Telegram bot
Yangi terminalda / In a new terminal:
```bash
python manage.py runbot
```

## API Endpoints

### Products
- `GET /api/v1/products/categories/` - Kategoriyalar ro'yxati / List categories
- `POST /api/v1/products/categories/` - Kategoriya qo'shish / Create category
- `GET /api/v1/products/products/` - Mahsulotlar ro'yxati / List products
- `POST /api/v1/products/products/` - Mahsulot qo'shish / Create product
- `GET /api/v1/products/products/{id}/` - Mahsulot ma'lumotlari / Product detail
- `PUT /api/v1/products/products/{id}/` - Mahsulotni yangilash / Update product
- `DELETE /api/v1/products/products/{id}/` - Mahsulotni o'chirish / Delete product

### Inventory
- `GET /api/v1/inventory/warehouses/` - Omborlar ro'yxati / List warehouses
- `POST /api/v1/inventory/warehouses/` - Ombor qo'shish / Create warehouse
- `GET /api/v1/inventory/stocks/` - Qoldiqlar ro'yxati / List stocks
- `GET /api/v1/inventory/stocks/low_stock/` - Kam qoldiqlar / Low stock items
- `POST /api/v1/inventory/stocks/` - Qoldiq qo'shish / Create stock
- `GET /api/v1/inventory/movements/` - Harakatlar tarixi / Movement history
- `POST /api/v1/inventory/movements/` - Harakat qo'shish / Create movement

## Admin Panel

Django admin panelga kirish / Access Django admin:
```
http://localhost:8000/admin/
```

## Telegram Bot Commandalari / Bot Commands

- `/start` - Botni ishga tushirish / Start the bot
- `📦 Mahsulotlar` - Mahsulotlar ro'yxati / View products
- `📊 Qoldiqlar` - Qoldiqlarni ko'rish / View stock levels
- `⚠️ Kam qoldiqlar` - Kam qoldiqlar ro'yxati / View low stock items
- `🏢 Omborlar` - Omborlar ro'yxati / View warehouses

## Ma'lumotlar strukturasi / Data Structure

### Product (Mahsulot)
- `name` - Nomi / Name
- `description` - Tavsif / Description
- `category` - Kategoriya / Category
- `price` - Narxi / Price
- `image` - Rasm / Image
- `barcode` - Shtrix-kod / Barcode
- `is_active` - Faolmi / Is active

### Stock (Qoldiq)
- `product` - Mahsulot / Product
- `warehouse` - Ombor / Warehouse
- `quantity` - Miqdor / Quantity
- `min_quantity` - Minimal miqdor / Minimum quantity

### StockMovement (Harakat)
- `stock` - Qoldiq / Stock
- `movement_type` - Harakat turi (IN/OUT/TRANSFER) / Movement type
- `quantity` - Miqdor / Quantity
- `note` - Izoh / Note

## Docker bilan ishga tushirish / Run with Docker

```bash
docker-compose up --build
```

## Muammolarni hal qilish / Troubleshooting

### Bot ishlamayapti / Bot not working
1. TELEGRAM_BOT_TOKEN to'g'ri o'rnatilganligini tekshiring / Check if TELEGRAM_BOT_TOKEN is set correctly
2. Bot BotFather orqali yaratilganligini va tokenni olganligini tekshiring / Verify bot is created via BotFather

### Database xatosi / Database error
1. PostgreSQL ishga tushganligini tekshiring / Check if PostgreSQL is running
2. Database ma'lumotlari to'g'riligini tekshiring / Verify database credentials

## Hissa qo'shish / Contributing

Pull requestlar qabul qilinadi!
Pull requests are welcome!

## Litsenziya / License

MIT
