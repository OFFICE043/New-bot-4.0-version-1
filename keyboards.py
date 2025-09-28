from telegram import ReplyKeyboardMarkup

# --- USER PANEL BUTTONS ---

# 1. Asosiy menyu
BTN_USER_ANIME_IZLASH = "🔍 Anime izlash"
BTN_USER_REKLAMA = "📢 Reklama"
BTN_USER_VIP = "⭐️ Vip"
BTN_USER_SUPPORT = "👨‍💻 Support"
BTN_USER_TO_ADMIN_PANEL = "⚙️ Admin panelga o'tish"

# 2. Anime izlash menyusi
BTN_ANIME_NOMI_ORQALI = "Nomi orqali izlash"
BTN_ANIME_KOD_ORQALI = "Kod orqali izlash"
BTN_ANIME_BARCHA = "Barcha animelar (VIP)"
BTN_ANIME_TOP20 = "TOP-20 ko'rilgan (VIP)"
BTN_ANIME_ADMIN_ORQALI = "Admin orqali izlash (VIP)"

# 3. Reklama menyusi
BTN_REKLAMA_OLISH = "Reklama olish"
BTN_REKLAMA_TAKLIF = "Reklama taklif qilish"

# 4. VIP menyusi
BTN_VIP_INFO = "VIPda nimalar bor?"


# --- ADMIN PANEL BUTTONS ---

# 1. Asosiy admin menyusi
BTN_ADMIN_ANIME_PANEL = "🎬 Anime paneli"
BTN_ADMIN_SOZLAMALAR_PANEL = "🛠 Sozlamalar paneli"
# ... (болашақта басқа админ батырмалары осында қосылады) ...
BTN_ADMIN_TO_USER_PANEL = "⬅️ User panelga qaytish"


# --- GENERAL BUTTONS ---
BTN_ORQAGA = "⬅️ Orqaga"


# === KEYBOARD LAYOUTS ===

# 1. USER PANEL KEYBOARDS

# Asosiy menyu (oddiy foydalanuvchi uchun)
user_main_menu_keyboard = ReplyKeyboardMarkup([
    [BTN_USER_ANIME_IZLASH],
    [BTN_USER_REKLAMA, BTN_USER_VIP],
    [BTN_USER_SUPPORT]
], resize_keyboard=True)

# Asosiy menyu (admin uchun)
admin_user_main_menu_keyboard = ReplyKeyboardMarkup([
    [BTN_USER_ANIME_IZLASH],
    [BTN_USER_REKLAMA, BTN_USER_VIP],
    [BTN_USER_SUPPORT],
    [BTN_USER_TO_ADMIN_PANEL] # Admin uchun qo'shimcha tugma
], resize_keyboard=True)

# Anime izlash menyusi
anime_search_menu_keyboard = ReplyKeyboardMarkup([
    [BTN_ANIME_NOMI_ORQALI],
    [BTN_ANIME_KOD_ORQALI],
    [BTN_ANIME_BARCHA],
    [BTN_ANIME_TOP20],
    [BTN_ANIME_ADMIN_ORQALI],
    [BTN_ORQAGA]
], resize_keyboard=True)

# Reklama menyusi
reklama_menu_keyboard = ReplyKeyboardMarkup([
    [BTN_REKLAMA_OLISH],
    [BTN_REKLAMA_TAKLIF],
    [BTN_ORQAGA]
], resize_keyboard=True)

# VIP menyusi
vip_menu_keyboard = ReplyKeyboardMarkup([
    [BTN_VIP_INFO],
    [BTN_ORQAGA]
], resize_keyboard=True)


# 2. ADMIN PANEL KEYBOARDS

# Asosiy admin menyusi
admin_main_menu_keyboard = ReplyKeyboardMarkup([
    [BTN_ADMIN_ANIME_PANEL],
    [BTN_ADMIN_SOZLAMALAR_PANEL],
    [BTN_ADMIN_TO_USER_PANEL]
], resize_keyboard=True)


# 3. GENERAL KEYBOARDS

# Orqaga qaytish uchun yagona tugma
back_keyboard = ReplyKeyboardMarkup([[BTN_ORQAGA]], resize_keyboard=True)

