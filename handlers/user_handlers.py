from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode

import database
import keyboards as kb

# Сөйлесу күйлерін (states) анықтаймыз
class UserStates:
    ANIME_SEARCH_NAME = 1
    ANIME_SEARCH_CODE = 2
    ANIME_SEARCH_VIA_ADMIN = 3
    REKLAMA_SUGGESTION = 4
    SUPPORT_TICKET = 5

# --- Көмекші функция: Админдерге хабарлама жіберу ---
async def notify_admins(context: ContextTypes.DEFAULT_TYPE, message: str):
    admin_ids = database.get_all_admins()
    for admin_id in admin_ids:
        try:
            await context.bot.send_message(chat_id=admin_id, text=message, parse_mode=ParseMode.HTML)
        except Exception as e:
            print(f"Admin {admin_id} ga xabar yuborishda xatolik: {e}")

# === НЕГІЗГІ МЕНЮ ХЭНДЛЕРЛЕРІ ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """/start командасын және негізгі менюге оралуды басқарады"""
    user = update.effective_user
    database.add_user(user_id=user.id, username=user.username, first_name=user.first_name)
    status = database.get_user_status(user.id)
    
    # VIP қолданушылар мен админдерге арнайы стикер жіберу
    if status in ['bosh_admin', 'oddiy_admin', 'vip']:
        # Бұл жерге қар анимациясы бар стикердің FILE_ID-сын қою керек
        # Мысалы: sticker_file_id = "CAACAgIAAxkBAAE..."
        # await context.bot.send_sticker(chat_id=user.id, sticker=sticker_file_id)
        pass

    if status == 'vip':
        welcome_text = f"Xush kelipsiz VIP a'zo, {user.mention_html()}!"
    else: # user, admin, bosh_admin
        welcome_text = f"Xush kelibsiz, {user.mention_html()}!"

    keyboard = kb.admin_user_main_menu_keyboard if status in ['bosh_admin', 'oddiy_admin'] else kb.user_main_menu_keyboard
    await update.message.reply_html(welcome_text, reply_markup=keyboard)
    
    # Кез келген диалогты тоқтату
    return ConversationHandler.END

async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Диалогты тоқтатып, негізгі менюге оралу"""
    await update.message.reply_text("Amal bekor qilindi.", reply_markup=kb.user_main_menu_keyboard)
    await start(update, context) # Негізгі менюді көрсету
    return ConversationHandler.END

# === ANIME IZLASH БӨЛІМІ ===

async def anime_search_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """'Anime izlash' менюін көрсетеді"""
    await update.message.reply_text("Qidiruv usulini tanlang:", reply_markup=kb.anime_search_menu_keyboard)

async def search_by_name_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Аты бойынша іздеуді бастайды"""
    await update.message.reply_text("Kerakli anime nomini yozing:", reply_markup=kb.back_keyboard)
    return UserStates.ANIME_SEARCH_NAME

async def process_name_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Жіберілген атты базадан іздеп, нәтижесін қайтарады"""
    results = database.search_anime_by_name(update.message.text)
    if not results:
        await update.message.reply_text("❌ Afsus, bunday nomli anime topilmadi.")
    else:
        response = "<b>🔍 Qidiruv natijalari:</b>\n\n"
        for code, name, desc in results:
            response += f"<b>Kodi:</b> <code>{code}</code>\n<b>Nomi:</b> {name}\n<b>Ta'rifi:</b> {desc or 'mavjud emas'}\n\n"
        await update.message.reply_html(response)
    # Іздеуден кейін қайтадан іздеу менюіне оралу
    await anime_search_menu(update, context)
    return ConversationHandler.END

async def search_by_code_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Коды бойынша іздеуді бастайды"""
    await update.message.reply_text("Kerakli anime kodini yozing:", reply_markup=kb.back_keyboard)
    return UserStates.ANIME_SEARCH_CODE

async def process_code_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    result = database.search_anime_by_code(update.message.text)
    if not result:
        await update.message.reply_text("❌ Afsus, bunday kodli anime topilmadi.")
    else:
        _id, code, name, desc = result
        await update.message.reply_html(f"<b>✅ Topildi:</b>\n\n<b>Kodi:</b> <code>{code}</code>\n<b>Nomi:</b> {name}\n<b>Ta'rifi:</b> {desc or 'mavjud emas'}")
    await anime_search_menu(update, context)
    return ConversationHandler.END
    
async def show_all_anime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status = database.get_user_status(update.effective_user.id)
    if status not in ['bosh_admin', 'oddiy_admin', 'vip']:
        await update.message.reply_text("❌ Bu funksiya faqat VIP a'zolar va Adminlar uchun.")
        return
    animes = database.get_all_anime()
    if not animes: 
        await update.message.reply_text("Hozircha bazada animelar mavjud emas.")
    else:
        response = "📄 <b>Barcha animelar ro'yxati:</b>\n\n" + "\n".join([f"<code>{c}</code> - {n}" for c, n in animes])
        await update.message.reply_html(response)

# ... (show_top_20 және admin_orqali_izlash функциялары ұқсас жасалады) ...

# === REKLAMA БӨЛІМІ ===

async def reklama_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """'Reklama' менюін көрсетеді"""
    await update.message.reply_text("Reklama bo'limi:", reply_markup=kb.reklama_menu_keyboard)

async def reklama_olish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "@anilordtvrek shu kanal dan Reklama narxi ni korish mumkin.\n\nAgar reklama olmoqchi bo'lsangiz, @username ga yozing."
    await update.message.reply_text(text)

# === VIP БӨЛІМІ ===

async def vip_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """'VIP' менюін көрсетеді"""
    await update.message.reply_text("VIP bo'limi:", reply_markup=kb.vip_menu_keyboard)

async def vip_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    vip_info_text = database.get_setting('vip_info')
    await update.message.reply_text(vip_info_text or "VIP haqida ma'lumot topilmadi.")

# === SUPPORT БӨЛІМІ ===

async def support_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Қолдау қызметімен диалогты бастайды"""
    text = "Agar jiddiy savol yoki yordam kerak bo'lsa, xabaringizni yozing.\n" \
           "Jiddiy bo'lmagan xabarlar uchun botdan chetlatilishingiz mumkin."
    await update.message.reply_text(text, reply_markup=kb.back_keyboard)
    return UserStates.SUPPORT_TICKET

async def process_support_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Қолданушының хабарламасын админдерге жібереді"""
    user = update.effective_user
    database.create_support_ticket(user_id=user.id, message=update.message.text)
    
    admin_message = (f"<b>‼️ Yangi yordam so'rovi</b>\n\n"
                     f"<b>Kimdan:</b> {user.mention_html()} (<code>{user.id}</code>)\n"
                     f"<b>Xabar:</b> {update.message.text}")
    await notify_admins(context, admin_message)
    
    await update.message.reply_text("✅ Xabaringiz adminlarga yuborildi. Tez orada javob berishadi.")
    
    # Диалогты аяқтап, негізгі менюге оралу
    await start(update, context)
    return ConversationHandler.END
