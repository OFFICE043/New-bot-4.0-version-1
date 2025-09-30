# handlers/user/support_vip.py
import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from database.db_manager import get_setting
from keyboards.user_keyboards import get_back_keyboard, get_main_menu_keyboard
from config import ADMIN_IDS
from .common_handlers import back_to_main_menu

logger = logging.getLogger(__name__)
WAITING_SUPPORT_MESSAGE = 0

async def vip_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    vip_desc = get_setting('vip_description') or "VIP a'zolik haqida ma'lumot hozircha kiritilmagan."
    await update.message.reply_text(vip_desc)

async def to_support_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = "Agar jiddiy savol yoki yordam kerak bo'lsa-gina yozing.\nQanday yordam kerakligini yozing:"
    await update.message.reply_text(text, reply_markup=get_back_keyboard())
    return WAITING_SUPPORT_MESSAGE

async def support_receive(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_info = f"Foydalanuvchi: {update.effective_user.mention_html()} (ID: {update.effective_user.id})"
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(admin_id, f"🆘 Yordam so'rovi (Support)!\n\n{user_info}\n\nMurojaat: {update.message.text}", parse_mode='HTML')
        except Exception as e:
            logger.error(f"Adminga {admin_id} support xabarini yuborishda xatolik: {e}")
    
    response = "✅ Xabaringiz yuborildi.\n⚠️ Eslatma: Agar xabaringiz jiddiy bo'lmasa, botdan chetlatilishingiz mumkin."
    await update.message.reply_text(response, reply_markup=get_main_menu_keyboard())
    return ConversationHandler.END

support_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^📞 Support$"), to_support_menu)],
    states={WAITING_SUPPORT_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, support_receive)]},
    fallbacks=[MessageHandler(filters.Regex("^⬅️ Orqaga$"), back_to_main_menu)],
)
