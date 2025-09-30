# config.py
import os
from dotenv import load_dotenv

# .env файлынан деректерді жүктеу
load_dotenv()

# Bot tokeni
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN .env faylida topilmadi!")

# PostgreSQL URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL .env faylida topilmadi!")

# Super Adminlar ID-lari
SUPER_ADMINS_STR = os.getenv("SUPER_ADMINS", "")
SUPER_ADMINS = [int(admin_id.strip()) for admin_id in SUPER_ADMINS_STR.split(',') if admin_id]

# VIP stiker ID-si
VIP_STICKER_ID = os.getenv("VIP_STICKER_ID")

# Admin ID-lari (хабарлама жіберу үшін)
# Шынайы жобада бұл ДБ-дан алынуы керек, бірақ жеделдету үшін осылай қалдырайық
ADMIN_IDS = SUPER_ADMINS 
