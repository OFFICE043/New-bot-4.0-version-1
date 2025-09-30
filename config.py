# config.py
import os
from dotenv import load_dotenv

# .env файлынан деректерді жүктеу
load_dotenv()

# Bot tokeni
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("DIQQAT: BOT_TOKEN .env faylida topilmadi!")

# PostgreSQL URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DIQQAT: DATABASE_URL .env faylida topilmadi!")

# Super Adminlar ID-lari
SUPER_ADMINS_STR = os.getenv("SUPER_ADMINS", "")
SUPER_ADMINS = [int(admin_id.strip()) for admin_id in SUPER_ADMINS_STR.split(',') if admin_id]
if not SUPER_ADMINS:
    raise ValueError("DIQQAT: SUPER_ADMINS .env faylida topilmadi!")
    
# VIP пайдаланушыларға арналған сәлемдесу стикерінің ID-сы
VIP_GREETING_STICKER_ID = os.getenv("VIP_GREETING_STICKER_ID")

# Admin ID-lari (хабарлама жіберу үшін)
ADMIN_IDS = SUPER_ADMINS
