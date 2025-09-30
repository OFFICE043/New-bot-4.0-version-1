# handlers/user/anime_search.py
import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from telegram.constants import ParseMode
from database.db_manager import find_anime_by_name, find_anime_by_code
from keyboards.user_keyboards import get_anime_search_keyboard, get_back_keyboard

# --- ЖАҢА ИМПОРТ ---
from .common_handlers import back_to_main_menu

logger = logging.getLogger(__name__)
SEARCH_BY_NAME, SEARCH_BY_CODE = range(2)

async def to_anime_search_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 Anime izlash bo'limi:", reply_markup=get_anime_search_keyboard())

# (Бұл жерден back_to_main_menu функциясы алынып тасталды)

# ... (Қалған барлық функциялар өзгеріссіз қалады) ...
async def search_by_name_start(update: Update, context: ContextTypes.DEFAULT_TYPE): #...
async def search_by_name_receive(update: Update, context: ContextTypes.DEFAULT_TYPE): #...
async def search_by_code_start(update: Update, context: ContextTypes.DEFAULT_TYPE): #...
async def search_by_code_receive(update: Update, context: ContextTypes.DEFAULT_TYPE): #...
async def all_animes(update: Update, context: ContextTypes.DEFAULT_TYPE): #...
async def top_animes(update: Update, context: ContextTypes.DEFAULT_TYPE): #...
async def search_via_admin(update: Update, context: ContextTypes.DEFAULT_TYPE): #...

anime_search_conv_handler = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Regex("^📝 Nomi orquali izlash$"), search_by_name_start),
        MessageHandler(filters.Regex("^🔢 Kod orquali izlash$"), search_by_code_start),
    ],
    states={
        SEARCH_BY_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex("^⬅️ Orqaga$"), search_by_name_receive)],
        SEARCH_BY_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex("^⬅️ Orqaga$"), search_by_code_receive)],
    },
    fallbacks=[MessageHandler(filters.Regex("^⬅️ Orqaga$"), back_to_main_menu)], # Енді бұл да дұрыс жұмыс істейді
)
