# handlers/user/reklama.py
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from keyboards.user_keyboards import get_back_keyboard, get_main_menu_keyboard
from config import ADMIN_IDS

# --- ЖАҢА ИМПОРТ ---
from .common_handlers import back_to_main_menu

logger = logging.getLogger(__name__)
GET_REKLAMA, SUGGEST_REKLAMA = range(2)

async def to_reklama_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Reklama olish"], ["Reklama taklif qilish"], ["⬅️ Orqaga"]]
    await update.message.reply_text(
        "📢 Reklama bo'limi:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def reklama_olish_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = (
        "Reklama narxlarini ko'rish uchun: @anilordtvrek\n\n"
        "Reklama olmoqchi bo'lsangiz, batafsil yozib yuboring (obuna kerakmi, qancha vaqtga va hokazo):"
    )
    await update.message.reply_text(text, reply_markup=get_back_keyboard())
    return GET_REKLAMA

async def reklama_olish_receive(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_info = f"Foydalanuvchi: {update.effective_user.mention_html()} (ID: {update.effective_user.id})"
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(admin_id, f"💸 Yangi reklama so'rovi!\n\n{user_info}\n\nXabar: {update.message.text}", parse_mode='HTML')
        except Exception as e:
            logger.error(f"Adminga {admin_id} reklama xabarini yuborishda xatolik: {e}")
    
    await update.message.reply_text("✅ Xabaringiz adminga yuborildi. Sizga albatta javob berishadi.", reply_markup=get_main_menu_keyboard())
    return ConversationHandler.END

# ... (Reklama taklif qilish функциясы да осыған ұқсас жасалады)

reklama_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^Reklama olish$"), reklama_olish_start)],
    states={
        GET_REKLAMA: [MessageHandler(filters.TEXT & ~filters.COMMAND & ~filters.Regex("^⬅️ Orqaga$"), reklama_olish_receive)]
    },
    fallbacks=[MessageHandler(filters.Regex("^⬅️ Orqaga$"), back_to_main_menu)] # Енді бұл дұрыс жұмыс істейді
)
