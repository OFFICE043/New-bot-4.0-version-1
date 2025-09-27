import os
from dotenv import load_dotenv

load_dotenv() # .env файлынан деректерді жүктейді

BOT_TOKEN = os.getenv("BOT_TOKEN")
# Бас админдердің ID-ларын осында үтір арқылы жазамыз
# Мысалы: "12345678,98765432"
HEAD_ADMINS_RAW = os.getenv("HEAD_ADMINS", "")
HEAD_ADMINS = [int(admin_id.strip()) for admin_id in HEAD_ADMINS_RAW.split(',') if admin_id.strip()]
