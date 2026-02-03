# 🏪 Store Bot - Ombor Boshqaruv Tizimi

Django asosidagi ombor boshqaruv tizimi Telegram bot integratsiyasi bilan.  
A Django-based warehouse management system with Telegram bot integration.

## 🚀 Xususiyatlar / Features

### Backend (Django REST API)
- ✅ **Mahsulotlar boshqaruvi** / Product management with categories
- ✅ **Ombor qoldiqlari** / Inventory tracking across multiple warehouses
- ✅ **Mahsulot harakati** / Stock movements (IN/OUT/TRANSFER)
- ✅ **Kam qoldiq ogohlantirishi** / Low stock alerts
- ✅ **REST API endpoints** with filtering and search
- ✅ **Django Admin panel** for easy management

### Telegram Bot
- 📦 **Mahsulotlar ro'yxati** / View products list
- 📊 **Qoldiqlarni tekshirish** / Check stock levels
- ⚠️ **Kam qoldiqlar** / Get low stock alerts
- 🏢 **Omborlar ro'yxati** / List warehouses
- 🔄 Real-time updates via Telegram

## 📋 Tizim talablari / Requirements

- Python 3.10+
- Django 6.0+
- PostgreSQL
- python-telegram-bot 21.0+

## ⚙️ O'rnatish / Installation

Batafsil o'rnatish va sozlash bo'yicha ko'rsatmalar:  
For detailed installation and setup instructions:

👉 **[SETUP.md](SETUP.md)** faylini o'qing / Read the SETUP.md file

### Tezkor boshlash / Quick Start

1. **Repositoriyani clone qiling / Clone the repository:**
```bash
git clone https://github.com/Boburshoh-oss/store-bot.git
cd store-bot
```

2. **Dependencieslarni o'rnating / Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **.env faylini yarating / Create .env file:**
```bash
cp .env-example .env
# Edit .env with your settings
```

4. **Migratsiyalarni bajaring / Run migrations:**
```bash
cd backend
python manage.py migrate
```

5. **Serverni ishga tushiring / Start the server:**
```bash
python manage.py runserver
```

6. **Telegram botni ishga tushiring / Start the bot:**
```bash
python manage.py runbot
```

## 📚 API Dokumentatsiyasi / API Documentation

Serverga kirganingizdan so'ng, Swagger UI orqali API dokumentatsiyasini ko'rishingiz mumkin:  
Once the server is running, you can access the API documentation via Swagger UI:

```
http://localhost:8000/swagger/
```

### Asosiy endpointlar / Main Endpoints

**Products:**
- `GET /api/v1/products/categories/` - Kategoriyalar
- `GET /api/v1/products/products/` - Mahsulotlar

**Inventory:**
- `GET /api/v1/inventory/warehouses/` - Omborlar
- `GET /api/v1/inventory/stocks/` - Qoldiqlar
- `GET /api/v1/inventory/stocks/low_stock/` - Kam qoldiqlar
- `GET /api/v1/inventory/movements/` - Harakat tarixi

## 🤖 Telegram Bot Sozlash / Telegram Bot Setup

1. [@BotFather](https://t.me/botfather) orqali bot yarating / Create a bot via @BotFather
2. Bot tokenini oling / Get the bot token
3. `.env` fayliga tokenni qo'shing / Add token to .env file:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
```
4. Botni ishga tushiring / Start the bot:
```bash
python manage.py runbot
```

## 🗂️ Loyiha strukturasi / Project Structure

```
store-bot/
├── backend/
│   ├── apps/
│   │   ├── products/      # Mahsulotlar / Products app
│   │   ├── inventory/     # Ombor / Inventory app
│   │   ├── bot/          # Telegram bot handlers
│   │   └── accounts/     # Foydalanuvchilar / User accounts
│   ├── config/           # Django sozlamalari / Settings
│   └── manage.py
├── requirements.txt      # Python dependencies
├── SETUP.md             # Batafsil o'rnatish / Detailed setup
└── README.md            # Bu fayl / This file
```

## 🛠️ Texnologiyalar / Technologies

- **Backend:** Django 6.0, Django REST Framework
- **Database:** PostgreSQL
- **Bot:** python-telegram-bot 21.0
- **API Docs:** drf-yasg (Swagger)
- **Authentication:** JWT, Token Auth

## 📸 Screenshots

_Coming soon..._

## 🤝 Hissa qo'shish / Contributing

Pull requestlar qabul qilinadi! / Pull requests are welcome!

1. Fork qiling / Fork the repository
2. Feature branch yarating / Create a feature branch
3. O'zgarishlaringizni commit qiling / Commit your changes
4. Branchni push qiling / Push to the branch
5. Pull Request oching / Open a Pull Request

## 📝 Litsenziya / License

MIT License - batafsil ma'lumot uchun [LICENSE](LICENSE) faylini ko'ring.

## 📧 Aloqa / Contact

**Developer:** Boburshoh  
**GitHub:** [@Boburshoh-oss](https://github.com/Boburshoh-oss)

---

⭐ Agar loyiha yoqsa, star bering! / If you like this project, give it a star!
