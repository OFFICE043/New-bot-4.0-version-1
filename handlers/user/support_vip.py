# handlers/user/support_vip.py
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from database.db_manager import get_setting

async def vip_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    vip_desc = get_setting('vip_description') or "VIP a'zolik haqida ma'lumot hozircha kiritilmagan."
    await update.message.reply_text(vip_desc)

# ... (Support функциясы да осында жасалады)
