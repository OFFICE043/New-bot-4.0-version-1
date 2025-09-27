from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
import database
import keyboards as kb

# States for conversations
class States:
    ANIME_SEARCH_NAME = 1
    ANIME_SEARCH_CODE = 2
    SUPPORT_TICKET = 3
    AD_SUGGESTION = 4
    # ... add other states as needed

# --- Helper Functions ---
async def notify_admins(context: ContextTypes.DEFAULT_TYPE, message: str):
    # This needs a function in database.py to get all admin ids
    # For now, we'll assume HEAD_ADMINS are the only ones to notify
    from config import HEAD_ADMINS
    for admin_id in HEAD_ADMINS:
        try:
            await context.bot.send_message(chat_id=admin_id, text=message, parse_mode=ParseMode.HTML)
        except Exception as e:
            print(f"Admin {admin_id} ga xabar yuborishda xatolik: {e}")

# --- Main Menu Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    database.add_user(user_id=user.id, username=user.username, first_name=user.first_name)
    status = database.get_user_status(user.id)
    
    keyboard = kb.admin_main_menu_keyboard if status in ['bosh_admin', 'oddiy_admin'] else kb.user_main_menu_keyboard
    await update.message.reply_html(f"Asosiy menyu, xush kelibsiz {user.mention_html()}!", reply_markup=keyboard)
    return ConversationHandler.END

# --- ANIME SEARCH ---
async def anime_search_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Qidiruv usulini tanlang:", reply_markup=kb.anime_search_menu_keyboard)

async def search_by_name_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Kerakli anime nomini yozing:", reply_markup=kb.cancel_keyboard)
    return States.ANIME_SEARCH_NAME

async def process_name_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    results = database.search_anime_by_name(update.message.text)
    if not results:
        await update.message.reply_text("❌ Afsus, bunday nomli anime topilmadi.")
    else:
        response = "🔍 Qidiruv natijalari:\n\n"
        for code, name, desc in results:
            response += f"<b>Kodi:</b> {code}\n<b>Nomi:</b> {name}\n<b>Ta'rifi:</b> {desc or 'mavjud emas'}\n\n"
        await update.message.reply_html(response)
    return await start(update, context)

async def search_by_code_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Kerakli anime kodini yozing:", reply_markup=kb.cancel_keyboard)
    return States.ANIME_SEARCH_CODE

async def process_code_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    result = database.search_anime_by_code(update.message.text)
    if not result:
        await update.message.reply_text("❌ Afsus, bunday kodli anime topilmadi.")
    else:
        code, name, desc = result
        await update.message.reply_html(f"✅ Topildi:\n\n<b>Kodi:</b> {code}\n<b>Nomi:</b> {name}\n<b>Ta'rifi:</b> {desc or 'mavjud emas'}")
    return await start(update, context)

async def show_all_anime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status = database.get_user_status(update.effective_user.id)
    if status not in ['bosh_admin', 'oddiy_admin', 'vip']:
        await update.message.reply_text("❌ Bu funksiya faqat VIP a'zolar va Adminlar uchun.")
        return
    animes = database.get_all_anime()
    if not animes:
        await update.message.reply_text("Hozircha bazada animelar mavjud emas.")
    else:
        response = " Barcha animelar ro'yxati:\n\n"
        response += "\n".join([f"<code>{code}</code> - {name}" for code, name in animes])
        await update.message.reply_html(response)

# ... (show_top_20 and search_via_admin would be similar with status checks) ...

# --- SUPPORT ---
async def support_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Agar jiddiy savol yoki yordam kerak bo'lsa, xabaringizni yozing.\n"
        "Jiddiy bo'lmagan xabarlar uchun botdan chetlatilishingiz mumkin.",
        reply_markup=kb.cancel_keyboard
    )
    return States.SUPPORT_TICKET

async def process_support_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    database.create_support_ticket(user_id=user.id, message=update.message.text)
    
    admin_message = (f"<b>Yangi yordam so'rovi!</b>\n\n"
                     f"<b>Foydalanuvchi:</b> {user.mention_html()} (<code>{user.id}</code>)\n"
                     f"<b>Xabar:</b> {update.message.text}")
    await notify_admins(context, admin_message)
    
    await update.message.reply_text("✅ Xabaringiz adminlarga yuborildi. Tez orada javob berishadi.")
    return await start(update, context)

# --- REKLAMA ---
async def reklama_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Reklama bo'limi:", reply_markup=kb.reklama_menu_keyboard)

async def get_ad_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # This text could also be moved to the database settings table
    text = "Reklama narxlarini ko'rish uchun @anilordtvrek kanaliga o'ting.\n\n" \
           "Buyurtma berish uchun, ushbu chatga kerakli reklama haqida to'liq ma'lumot yozing (obuna kerakmi, vaqti va h.k.)."
    await update.message.reply_text(text)
    # Here you could start another conversation state to handle the ad purchase process

# --- VIP ---
async def vip_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("VIP bo'limi:", reply_markup=kb.vip_menu_keyboard)

async def get_vip_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    vip_info_text = database.get_setting('vip_info')
    await update.message.reply_text(vip_info_text or "VIP haqida ma'lumot topilmadi.")
