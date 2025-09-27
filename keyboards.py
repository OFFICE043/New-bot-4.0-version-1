from telegram import ReplyKeyboardMarkup

# === USER PANEL BUTTONS ===
BTN_ANIME_SEARCH = "🔍 Anime izlash"
BTN_REKLAMA = "📢 Reklama"
BTN_VIP = "⭐️ Vip"
BTN_SUPPORT = "👨‍💻 Support"
BTN_TO_ADMIN_PANEL = "⚙️ Admin panelga o'tish"
BTN_SEARCH_BY_NAME = "Nomi orqali izlash"
BTN_SEARCH_BY_CODE = "Kod orqali izlash"
# ... (user panel buttons) ...

# === ADMIN PANEL BUTTONS ===
BTN_ANIME_PANEL = "🎬 Anime panel"
BTN_SETTINGS_PANEL = "⚙️ Sozlamalar paneli"
BTN_BROADCAST = "📤 Habar yuborish"
BTN_MANAGE_ADMINS = "👥 Adminlarni boshqarish"
BTN_GET_DB = "💾 Bazani olish"
BTN_TO_USER_PANEL = "⬅️ User panelga qaytish"
# Anime Panel Submenu
BTN_ADD_ANIME = "➕ Anime qo'shish"
BTN_DELETE_ANIME = "❌ Anime o'chirish"
BTN_LIST_ANIME = "📄 Animelar ro'yxati"
BTN_STATS = "📊 Statistika"
# Manage Admins Submenu
BTN_ADD_ADMIN = "➕ Admin qo'shish"
BTN_REMOVE_ADMIN = "➖ Adminni o'chirish"
BTN_LIST_ADMINS = "📋 Adminlar ro'yxati"

# === GENERAL BUTTONS ===
BTN_BACK_TO_MAIN_ADMIN_PANEL = "⬅️ Admin panelga"
BTN_CANCEL = "❌ Bekor qilish"

# === KEYBOARD LAYOUTS ===
# ... (user keyboards remain the same) ...
user_main_menu_keyboard = ReplyKeyboardMarkup([
    [BTN_ANIME_SEARCH], [BTN_REKLAMA, BTN_VIP], [BTN_SUPPORT]
], resize_keyboard=True)

admin_main_menu_keyboard = ReplyKeyboardMarkup([
    [BTN_ANIME_SEARCH], [BTN_REKLAMA, BTN_VIP], [BTN_SUPPORT], [BTN_TO_ADMIN_PANEL]
], resize_keyboard=True)

# Admin Panel Main Menu
admin_panel_main_menu_keyboard = ReplyKeyboardMarkup([
    [BTN_ANIME_PANEL, BTN_SETTINGS_PANEL],
    [BTN_BROADCAST, BTN_MANAGE_ADMINS],
    [BTN_GET_DB],
    [BTN_TO_USER_PANEL]
], resize_keyboard=True)

# Anime Panel Menu
anime_panel_menu_keyboard = ReplyKeyboardMarkup([
    [BTN_ADD_ANIME, BTN_DELETE_ANIME],
    [BTN_LIST_ANIME, BTN_STATS],
    [BTN_BACK_TO_MAIN_ADMIN_PANEL]
], resize_keyboard=True)

# Manage Admins Menu
manage_admins_menu_keyboard = ReplyKeyboardMarkup([
    [BTN_ADD_ADMIN, BTN_REMOVE_ADMIN],
    [BTN_LIST_ADMINS],
    [BTN_BACK_TO_MAIN_ADMIN_PANEL]
], resize_keyboard=True)

# Cancel Keyboard
cancel_keyboard = ReplyKeyboardMarkup([[BTN_CANCEL]], resize_keyboard=True)
