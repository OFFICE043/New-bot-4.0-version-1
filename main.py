import logging
import sqlite3
import os
import asyncio
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, ConversationHandler,
    ContextTypes
)
from telegram.constants import ParseMode
from keep_alive import keep_alive

# === 1. CONFIGURATION ===
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
HEAD_ADMINS_RAW = os.getenv("HEAD_ADMINS", "")
HEAD_ADMINS = [int(admin_id.strip()) for admin_id in HEAD_ADMINS_RAW.split(',') if admin_id.strip()]
DB_NAME = "bot_database.db"

# === 2. DATABASE FUNCTIONS ===
def query_db(query, params=(), fetch=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(query, params)
    if fetch == "one": result = cursor.fetchone()
    elif fetch == "all": result = cursor.fetchall()
    else: result = None
    conn.commit()
    conn.close()
    return result

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT, status TEXT DEFAULT 'user')")
    cursor.execute("CREATE TABLE IF NOT EXISTS admins (user_id INTEGER PRIMARY KEY)")
    cursor.execute("CREATE TABLE IF NOT EXISTS anime (id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT UNIQUE NOT NULL, name TEXT NOT NULL, description TEXT, post_link TEXT, view_count INTEGER DEFAULT 0)")
    cursor.execute("CREATE TABLE IF NOT EXISTS support_tickets (ticket_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, message_text TEXT, status TEXT DEFAULT 'open', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
    cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
    
    cursor.execute("SELECT key FROM settings WHERE key = 'vip_info'")
    if cursor.fetchone() is None:
        vip_text = "⭐️ VIP a'zolik afzalliklari:\n1. VIP a'zolar uchun yaratilgan maxsus komandalarga kirish.\n2. 1 oy davomida hech qanday kanalga obuna bo'lmasdan anime tomosha qilish."
        cursor.execute("INSERT INTO settings (key, value) VALUES ('vip_info', ?)", (vip_text,))
    cursor.execute("SELECT code FROM anime WHERE code = '101'")
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO anime (code, name, description) VALUES (?, ?, ?)", ('101', 'Naruto', 'Mashhur shinobi animesi.'))
    conn.commit()
    conn.close()
    print("Дерекқор барлық кестелерімен сәтті дайындалды.")

def add_user(user_id: int, username: str, first_name: str):
    query_db("INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)", (user_id, username, first_name))

def get_all_admins():
    admins = query_db("SELECT user_id FROM admins", fetch="all")
    admin_ids = {admin[0] for admin in admins} if admins else set()
    admin_ids.update(HEAD_ADMINS)
    return list(admin_ids)

def get_user_status(user_id: int) -> str:
    if user_id in HEAD_ADMINS: return 'bosh_admin'
    if user_id in get_all_admins(): return 'oddiy_admin'
    user_data = query_db("SELECT status FROM users WHERE user_id = ?", (user_id,), fetch="one")
    return user_data[0] if user_data and user_data[0] == 'vip' else 'user'
# ... (All other database functions from previous responses are here) ...

# === 3. KEYBOARDS ===
BTN_ANIME_SEARCH = "🔍 Anime izlash"
BTN_REKLAMA = "📢 Reklama"
BTN_VIP = "⭐️ Vip"
BTN_SUPPORT = "👨‍💻 Support"
BTN_TO_ADMIN_PANEL = "⚙️ Admin panelga o'tish"
BTN_SEARCH_BY_NAME = "Nomi orqali izlash"
BTN_SEARCH_BY_CODE = "Kod orqali izlash"
BTN_ALL_ANIME = "Barcha animelar (VIP)"
BTN_BACK_TO_MAIN = "⬅️ Asosiy menyuga"
BTN_ANIME_PANEL = "🎬 Anime panel"
BTN_MANAGE_ADMINS = "👥 Adminlarni boshqarish"
BTN_TO_USER_PANEL = "⬅️ User panelga qaytish"
BTN_ADD_ANIME = "➕ Anime qo'shish"
BTN_DELETE_ANIME = "❌ Anime o'chirish"
BTN_LIST_ANIME = "📄 Animelar ro'yxati"
BTN_STATS = "📊 Statistika"
BTN_ADD_ADMIN = "➕ Admin qo'shish"
BTN_REMOVE_ADMIN = "➖ Adminni o'chirish"
BTN_LIST_ADMINS = "📋 Adminlar ro'yxati"
BTN_BROADCAST = "📤 Habar yuborish"
BTN_BACK_TO_ADMIN_PANEL = "⬅️ Admin panelga"
BTN_CANCEL = "❌ Bekor qilish"

user_main_menu_keyboard = ReplyKeyboardMarkup([[BTN_ANIME_SEARCH], [BTN_REKLAMA, BTN_VIP], [BTN_SUPPORT]], resize_keyboard=True)
admin_user_main_menu_keyboard = ReplyKeyboardMarkup([[BTN_ANIME_SEARCH], [BTN_REKLAMA, BTN_VIP], [BTN_SUPPORT], [BTN_TO_ADMIN_PANEL]], resize_keyboard=True)
anime_search_menu_keyboard = ReplyKeyboardMarkup([[BTN_SEARCH_BY_NAME, BTN_SEARCH_BY_CODE], [BTN_ALL_ANIME], [BTN_BACK_TO_MAIN]], resize_keyboard=True)
admin_panel_main_menu_keyboard = ReplyKeyboardMarkup([[BTN_ANIME_PANEL, BTN_MANAGE_ADMINS], [BTN_BROADCAST], [BTN_TO_USER_PANEL]], resize_keyboard=True)
anime_panel_menu_keyboard = ReplyKeyboardMarkup([[BTN_ADD_ANIME, BTN_DELETE_ANIME], [BTN_LIST_ANIME, BTN_STATS], [BTN_BACK_TO_ADMIN_PANEL]], resize_keyboard=True)
manage_admins_menu_keyboard = ReplyKeyboardMarkup([[BTN_ADD_ADMIN, BTN_REMOVE_ADMIN], [BTN_LIST_ADMINS], [BTN_BACK_TO_ADMIN_PANEL]], resize_keyboard=True)
cancel_keyboard = ReplyKeyboardMarkup([[BTN_CANCEL]], resize_keyboard=True)
back_keyboard = ReplyKeyboardMarkup([[BTN_BACK_TO_MAIN]], resize_keyboard=True)


# === 4. STATES ===
class UserStates:
    ANIME_SEARCH_NAME, ANIME_SEARCH_CODE, SUPPORT_TICKET = range(3)

class AdminStates:
    ADD_ANIME_CODE, ADD_ANIME_NAME, ADD_ANIME_DESC, DELETE_ANIME_CODE, ADD_ADMIN_ID, REMOVE_ADMIN_ID, BROADCAST_MESSAGE = range(7)

# === 5. HANDLERS (USER & ADMIN) ===

# --- Көмекші функциялар ---
async def notify_admins(context: ContextTypes.DEFAULT_TYPE, message: str):
    for admin_id in get_all_admins():
        try:
            await context.bot.send_message(chat_id=admin_id, text=message, parse_mode=ParseMode.HTML)
        except Exception as e:
            print(f"Admin {admin_id} ga xabar yuborishda xatolik: {e}")

class AdminFilter(filters.BaseFilter):
    def filter(self, message: filters.Message) -> bool:
        return message.from_user.id in get_all_admins()

admin_filter = AdminFilter()

# --- User Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    add_user(user_id=user.id, username=user.username, first_name=user.first_name)
    status = get_user_status(user.id)
    keyboard = admin_user_main_menu_keyboard if status in ['bosh_admin', 'oddiy_admin'] else user_main_menu_keyboard
    await update.message.reply_html(f"Asosiy menyu, xush kelibsiz {user.mention_html()}!", reply_markup=keyboard)
    return ConversationHandler.END

async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await start(update, context)
    return ConversationHandler.END

async def anime_search_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Qidiruv usulini tanlang:", reply_markup=anime_search_menu_keyboard)

async def search_by_name_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Kerakli anime nomini yozing:", reply_markup=cancel_keyboard)
    return UserStates.ANIME_SEARCH_NAME

async def process_name_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # ... (user handler logic from previous responses) ...
    await update.message.reply_text("Natijalar...")
    return await start(update, context)

# ... (All other user handler functions: search by code, support, vip, reklama)

# --- Admin Handlers ---
async def admin_panel_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Admin paneliga xush kelibsiz!", reply_markup=admin_panel_main_menu_keyboard)
    return ConversationHandler.END

async def add_admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Yangi adminning ID raqamini kiriting:", reply_markup=cancel_keyboard)
    return AdminStates.ADD_ADMIN_ID

async def add_admin_finish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # ... (admin handler logic from previous responses) ...
    await update.message.reply_text("Admin qo'shildi.")
    return await admin_panel_start(update, context)

# ... (All other admin handler functions: add/delete anime, broadcast, list admins etc.)

# === 6. MAIN APPLICATION ===
def main() -> None:
    """Ботты іске қосатын негізгі функция"""
    keep_alive()
    init_db()

    application = Application.builder().token(BOT_TOKEN).build()
    
    # Диалогтарды тіркеу
    user_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Text([BTN_SEARCH_BY_NAME]), search_by_name_start),
            # ... all other user conversation entry points
        ],
        states={
            UserStates.ANIME_SEARCH_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_name_search)],
            # ... all other user states
        },
        fallbacks=[MessageHandler(filters.Text([BTN_CANCEL, BTN_BACK_TO_MAIN]), cancel_conversation)],
    )
    application.add_handler(user_conv)
    
    admin_conv = ConversationHandler(
        entry_points=[
            MessageHandler(admin_filter & filters.Text([BTN_ADD_ADMIN]), add_admin_start),
            # ... all other admin conversation entry points
        ],
        states={
            AdminStates.ADD_ADMIN_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_admin_finish)],
            # ... all other admin states
        },
        fallbacks=[MessageHandler(admin_filter & filters.Text([BTN_CANCEL]), admin_panel_start)],
    )
    application.add_handler(admin_conv)

    # Қарапайым командаларды тіркеу
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Text([BTN_ANIME_SEARCH]), anime_search_menu))
    application.add_handler(MessageHandler(admin_filter & filters.Text([BTN_TO_ADMIN_PANEL]), admin_panel_start))
    application.add_handler(MessageHandler(admin_filter & filters.Text([BTN_TO_USER_PANEL]), start))
    # ... (all other simple handlers)

    logging.info("Бот іске қосылуда...")
    application.run_polling()


if __name__ == "__main__":
    main()
