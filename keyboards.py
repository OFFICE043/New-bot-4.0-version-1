from telegram import ReplyKeyboardMarkup

# --- Батырмалардың мәтіндері (Өзбекше, Латынша) ---

# Негізгі меню батырмалары
BTN_ANIME_SEARCH = "🔍 Anime izlash"
BTN_REKLAMA = "📢 Reklama"
BTN_VIP = "⭐️ Vip"
BTN_SUPPORT = "👨‍💻 Support"
BTN_TO_ADMIN_PANEL = "⚙️ Admin panelga o'tish"

# Жалпы батырмалар
BTN_BACK = "⬅️ Orqaga"

# --- Меню дизайндары (Keyboard Layouts) ---

# Қарапайым қолданушының негізгі менюі
user_main_menu_layout = [
    [BTN_ANIME_SEARCH],
    [BTN_REKLAMA, BTN_VIP],
    [BTN_SUPPORT]
]
# Жоғарыдағы дизайн бойынша дайын клавиатура
user_main_menu_keyboard = ReplyKeyboardMarkup(user_main_menu_layout, resize_keyboard=True)


# Админнің негізгі менюі (қолданушынікі + админ кнопкасы)
admin_main_menu_layout = [
    [BTN_ANIME_SEARCH],
    [BTN_REKLAMA, BTN_VIP],
    [BTN_SUPPORT],
    [BTN_TO_ADMIN_PANEL] # Админге арналған қосымша кнопка
]
# Админге арналған дайын клавиатура
admin_main_menu_keyboard = ReplyKeyboardMarkup(admin_main_menu_layout, resize_keyboard=True)


# "Артқа" кнопкасы бар клавиатура
back_keyboard_layout = [[BTN_BACK]]
back_keyboard = ReplyKeyboardMarkup(back_keyboard_layout, resize_keyboard=True)
