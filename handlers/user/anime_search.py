# handlers/user/anime_search.py

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)
from telegram.constants import ParseMode

from database.db_manager import find_anime_by_name, find_anime_by_code, get_all_animes_paginated, get_top_viewed_animes, get_user_role
from keyboards.user_keyboards import get_anime_search_keyboard, get_back_keyboard, get_main_menu_keyboard
from config import ADMIN_IDS

# Логгер
logger = logging.getLogger(__name__)

# ConversationHandler күйлері
SEARCH_BY_NAME, SEARCH_BY_CODE, SEARCH_VIA_ADMIN = range(3)

# --- Негізгі навигация ---

async def to_anime_search_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """'🎬 Anime Izlash' батырмасын басқанда осы функция іске қосылады."""
    await update.message.reply_text(
        "🎬 Anime izlash bo'limi. Kerakli buyruqni tanlang:",
        reply_markup=get_anime_search_keyboard()
    )

async def back_to_main_menu_from_convo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Диалог ішінен негізгі менюге оралу."""
    await update.message.reply_text(
        "Asosiy menyuga qaytdingiz.",
        reply_markup=get_main_menu_keyboard()
    )
    return ConversationHandler.END

async def back_to_main_menu_from_regular(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Қарапайым менюден негізгі менюге оралу."""
    await update.message.reply_text(
        "Asosiy menyuga qaytdingiz.",
        reply_markup=get_main_menu_keyboard()
    )

# --- Аты бойынша іздеу ---

async def search_by_name_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Izlash uchun anime nomini yozing:", reply_markup=get_back_keyboard())
    return SEARCH_BY_NAME

async def search_by_name_receive(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    anime_name = update.message.text
    anime = find_anime_by_name(anime_name)
    
    if anime:
        response = f"✅ Topildi!\n\n🎬 *Nomi:* {anime['name']}\n🔢 *Kodi:* `{anime['code']}`\n📄 *Tavsif:* {anime['description'] or 'Mavjud emas'}"
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=get_anime_search_keyboard())
    else:
        await update.message.reply_text("❌ Afsus, bunday nomdagi anime topilmadi.", reply_markup=get_anime_search_keyboard())
        
    return ConversationHandler.END

# --- Коды бойынша іздеу ---

async def search_by_code_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Izlash uchun anime kodini yozing (Masalan: A001):", reply_markup=get_back_keyboard())
    return SEARCH_BY_CODE

async def search_by_code_receive(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    anime_code = update.message.text
    anime = find_anime_by_code(anime_code)
        
    if anime:
        response = f"✅ Topildi!\n\n🎬 *Nomi:* {anime['name']}\n🔢 *Kodi:* `{anime['code']}`\n📄 *Tavsif:* {anime['description'] or 'Mavjud emas'}"
        await update.message.reply_text(response, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=get_anime_search_keyboard())
    else:
        await update.message.reply_text("❌ Afsus, bunday kodli anime topilmadi.", reply_markup=get_anime_search_keyboard())

    return ConversationHandler.END

# --- Қалған функциялар ---

async def all_animes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    role = get_user_role(update.effective_user.id)
    if role not in ['vip', 'admin']:
        await update.message.reply_text("Bu bo'lim faqat VIP a'zo yoki Adminlar uchun.")
        return
    # TODO: Беттеу (пагинация) логикасын осында қосу керек

async def top_animes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    role = get_user_role(update.effective_user.id)
    if role not in ['vip', 'admin']:
        await update.message.reply_text("Bu bo'lim faqat VIP a'zo yoki Adminlar uchun.")
        return
    # TODO: Ең көп көрілгендерді ДБ-дан алу логикасы

async def search_via_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
     # TODO: Админ арқылы іздеу диалогы
    await update.message.reply_text("Bu funksiya tez orada ishga tushadi.")


# --- Conversation Handler-ді дұрыс құру ---
anime_search_conv_handler = ConversationHandler(
    entry_points=[
        MessageHandler(filters.Regex("^📝 Nomi orquali izlash$"), search_by_name_start),
        MessageHandler(filters.Regex("^🔢 Kod orquali izlash$"), search_by_code_start),
    ],
    states={
        SEARCH_BY_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex("^⬅️ Orqaga$"), search_by_name_receive)],
        SEARCH_BY_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex("^⬅️ Orqaga$"), search_by_code_receive)],
    },
    fallbacks=[MessageHandler(filters.Regex("^⬅️ Orqaga$"), back_to_main_menu_from_convo)],
)

