# keyboards/user_keyboards.py
from telegram import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Негізгі меню батырмалары."""
    keyboard = [
        [KeyboardButton("🎬 Anime Izlash"), KeyboardButton("📢 Reklama")],
        [KeyboardButton("👑 VIP"), KeyboardButton("📞 Support")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_anime_search_keyboard() -> ReplyKeyboardMarkup:
    """Аниме іздеу менюінің батырмалары."""
    keyboard = [
        [KeyboardButton("📝 Nomi orquali izlash"), KeyboardButton("🔢 Kod orquali izlash")],
        [KeyboardButton("📚 Barcha animelar"), KeyboardButton("🏆 Ko'p ko'rilgan 20 anime")],
        [KeyboardButton("🧑‍💻 Admin orquali izlash")],
        [KeyboardButton("⬅️ Orqaga")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
def get_back_keyboard() -> ReplyKeyboardMarkup:
    """Тек "Артқа" батырмасы бар меню."""
    return ReplyKeyboardMarkup([[KeyboardButton("⬅️ Orqaga")]], resize_keyboard=True)
