# keyboards/admin_keyboards.py
from telegram import ReplyKeyboardMarkup, KeyboardButton

def get_admin_main_keyboard() -> ReplyKeyboardMarkup:
    """Негізгі админ панелінің батырмалары."""
    keyboard = [
        [KeyboardButton("🎬 Anime Panel"), KeyboardButton("⚙️ Sozlamalar Panel")],
        [KeyboardButton("📬 Habar Yuborish"), KeyboardButton("👮 Admin Boshqarish")],
        [KeyboardButton("🗄️ Bazani Olish"), KeyboardButton("📤 Baza Yuklash")],
        [KeyboardButton("👤 User Panelga o'tish")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
