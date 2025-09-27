from telegram import ReplyKeyboardMarkup, KeyboardButton

# --- Button Texts ---
# Main Menu
BTN_ANIME_SEARCH = "🔍 Anime izlash"
BTN_REKLAMA = "📢 Reklama"
BTN_VIP = "⭐️ Vip"
BTN_SUPPORT = "👨‍💻 Support"
BTN_TO_ADMIN_PANEL = "⚙️ Admin panelga o'tish"

# Anime Search Menu
BTN_SEARCH_BY_NAME = "Nomi orqali izlash"
BTN_SEARCH_BY_CODE = "Kod orqali izlash"
BTN_ALL_ANIME = "Barcha animelar"
BTN_TOP_20 = "TOP-20 animelar"
BTN_SEARCH_VIA_ADMIN = "Admin orqali izlash"

# Reklama Menu
BTN_GET_AD = "Reklama olish"
BTN_SUGGEST_AD = "Reklama taklif qilish"

# VIP Menu
BTN_VIP_INFO = "VIPda nimalar bor?"

# General Buttons
BTN_BACK_TO_MAIN = "⬅️ Asosiy menyuga"
BTN_CANCEL = "❌ Bekor qilish"

# --- Keyboard Layouts ---

# User Main Menu
user_main_menu_keyboard = ReplyKeyboardMarkup([
    [BTN_ANIME_SEARCH], [BTN_REKLAMA, BTN_VIP], [BTN_SUPPORT]
], resize_keyboard=True)

# Admin Main Menu
admin_main_menu_keyboard = ReplyKeyboardMarkup([
    [BTN_ANIME_SEARCH], [BTN_REKLAMA, BTN_VIP], [BTN_SUPPORT], [BTN_TO_ADMIN_PANEL]
], resize_keyboard=True)

# Anime Search Menu
anime_search_menu_keyboard = ReplyKeyboardMarkup([
    [BTN_SEARCH_BY_NAME, BTN_SEARCH_BY_CODE],
    [BTN_ALL_ANIME, BTN_TOP_20],
    [BTN_SEARCH_VIA_ADMIN],
    [BTN_BACK_TO_MAIN]
], resize_keyboard=True)

# Reklama Menu
reklama_menu_keyboard = ReplyKeyboardMarkup([
    [BTN_GET_AD], [BTN_SUGGEST_AD], [BTN_BACK_TO_MAIN]
], resize_keyboard=True)

# VIP Menu
vip_menu_keyboard = ReplyKeyboardMarkup([
    [BTN_VIP_INFO], [BTN_BACK_TO_MAIN]
], resize_keyboard=True)

# Cancel Keyboard (for conversations)
cancel_keyboard = ReplyKeyboardMarkup([[BTN_CANCEL]], resize_keyboard=True)
