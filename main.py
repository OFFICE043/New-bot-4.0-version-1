# main.py
import logging
import os
from dotenv import load_dotenv

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# .env файлынан BOT_TOKEN оқу (қауіпсіздік үшін)
# Жобаның қасында .env деген файл жасап, ішіне BOT_TOKEN='СІЗДІҢ_ТОКЕНІҢІЗ' деп жазыңыз
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Логгингті қосу (қателерді көру үшін)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Mock Data (Деректер базасының орнына уақытша деректер) ---

# Пайдаланушылардың ID-лары және олардың рөлдері (admin, vip, user)
# Шынайы жобада бұл деректер базасында сақталады (PostgreSQL, SQLite, т.б.)
USERS_DB = {
    7483732504: {"role": "admin"},  # Админ ID мысалы
    7535577228: {"role": "vip"},     # VIP ID мысалы
    7291451094: {"role": "user"},   # Қарапайым пайдаланушы ID мысалы
}

# Админдердің ID тізімі (хабарлама жіберу үшін)
ADMIN_IDS = [7483732504] # Осы жерге өз админ ID-леріңізді жазыңыз

# Анимелердің уақытша базасы
ANIME_DB = {
    "1": {"code": "A001", "name": "Naruto", "description": "Shinobi dunyosi haqida anime.", "views": 1500},
    "2": {"code": "A002", "name": "Bleach", "description": "Shinigamilar haqida anime.", "views": 1200},
    "3": {"code": "A003", "name": "One Piece", "description": "Qaroqchilar qiroli bo'lish haqida.", "views": 2500},
    "4": {"code": "B001", "name": "Attack on Titan", "description": "Odamzod va titanlar kurashi.", "views": 1800},
    "5": {"code": "C005", "name": "Death Note", "description": "Adolat uchun o'lim daftari.", "views": 2100},
    # ... тағы 20-30 аниме қосуға болады
}

# VIP пайдаланушылар үшін жіберілетін анимациялық стикердің File ID-сы
# Бұл ID-ді алу үшін стикерді @RawDataBot сияқты ботқа жіберіңіз
VIP_WELCOME_STICKER_ID = "CAACAgIAAxkBAAEj03Zl-YcxA0gVGt0p-5g0b5GJdF8pAwACeAcAAlw_CQc2Wd5PZXzm1zQE"

# --- ConversationHandler үшін күйлер (состояния) ---
# Бұл сатылы диалогтарды басқаруға арналған константалар
(ANIME_MENU, REKLAMA_MENU, VIP_MENU, SUPPORT_MENU, ADMIN_PANEL) = range(5)
(SEARCH_BY_NAME, SEARCH_BY_CODE, SEARCH_VIA_ADMIN) = range(5, 8)
(GET_REKLAMA, SUGGEST_REKLAMA) = range(8, 10)
WAITING_SUPPORT_MESSAGE = 10

# --- Көмекші функциялар ---

def get_user_role(user_id: int) -> str:
    """Пайдаланушының рөлін (admin, vip, user) анықтайды."""
    if user_id in ADMIN_IDS:
        # Егер админдер тізімінде болса, бірақ базада жоқ болса, қосамыз
        if user_id not in USERS_DB:
            USERS_DB[user_id] = {"role": "admin"}
        return "admin"
    return USERS_DB.get(user_id, {}).get("role", "user")

# --- Негізгі меню батырмаларын жасайтын функция ---

def get_main_menu_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    """Пайдаланушы рөліне қарай негізгі менюді құрастырады."""
    keyboard = [
        [KeyboardButton("Anime Izlash"), KeyboardButton("Reklama")],
        [KeyboardButton("VIP"), KeyboardButton("Support")],
    ]
    if get_user_role(user_id) == "admin":
        keyboard.append([KeyboardButton("ADMIN PANELIGA O'TISH")])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# --- 'Orqaga' (Артқа) батырмасы бар менюлер ---

def get_anime_menu_keyboard() -> ReplyKeyboardMarkup:
    """'Anime Izlash' ішіндегі менюді құрастырады."""
    keyboard = [
        [KeyboardButton("Nomi orqali izlash"), KeyboardButton("Kod orqali izlash")],
        [KeyboardButton("Barcha animelar"), KeyboardButton("Ko'p ko'rilgan 20 anime")],
        [KeyboardButton("Admin orqali izlash")],
        [KeyboardButton("Orqaga")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_reklama_menu_keyboard() -> ReplyKeyboardMarkup:
    """'Reklama' ішіндегі менюді құрастырады."""
    keyboard = [
        [KeyboardButton("Reklama olish"), KeyboardButton("Reklama taklif qilish")],
        [KeyboardButton("Orqaga")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
def get_vip_menu_keyboard() -> ReplyKeyboardMarkup:
    """'VIP' ішіндегі менюді құрастырады."""
    keyboard = [
        [KeyboardButton("VIPda nimalar bor?")],
        [KeyboardButton("Orqaga")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_back_keyboard() -> ReplyKeyboardMarkup:
    """Тек 'Orqaga' батырмасы бар менюді қайтарады."""
    return ReplyKeyboardMarkup([[KeyboardButton("Orqaga")]], resize_keyboard=True)


# --- Негізгі хендлерлер (Командаларды өңдеушілер) ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start командасын өңдейді. Жаңа пайдаланушыны тіркейді және рөліне қарай сәлемдесу жібереді."""
    user = update.effective_user
    user_id = user.id
    
    # Егер пайдаланушы базада жоқ болса, оны 'user' ретінде қосамыз
    if user_id not in USERS_DB:
        USERS_DB[user_id] = {"role": "user"}
        logger.info(f"Yangi foydalanuvchi qo'shildi: {user_id}")

    role = get_user_role(user_id)
    welcome_message = ""
    
    # Рөлге байланысты сәлемдесу мәтінін таңдау
    if role == "admin":
        welcome_message = f"Xush kelibsiz, hurmatli Admin {user.mention_html()}!"
    elif role == "vip":
        # VIP пайдаланушыға арнайы стикер жіберу
        await context.bot.send_sticker(chat_id=user_id, sticker=VIP_WELCOME_STICKER_ID)
        welcome_message = f"Xush kelibsiz, VIP a'zo {user.mention_html()}!"
    else:
        welcome_message = f"Xush kelibsiz, {user.mention_html()}!"

    await update.message.reply_html(
        welcome_message,
        reply_markup=get_main_menu_keyboard(user_id),
    )

async def back_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Кез келген менюден негізгі менюге оралу функциясы."""
    user_id = update.effective_user.id
    await update.message.reply_text(
        "Asosiy menyudasiz.",
        reply_markup=get_main_menu_keyboard(user_id)
    )
    # Егер ConversationHandler ішінде болса, оны тоқтатады
    return ConversationHandler.END


# --- 'Anime Izlash' менюінің хендлерлері ---

async def anime_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """'Anime Izlash' менюін көрсетеді."""
    await update.message.reply_text(
        "Anime izlash bo'limi. Kerakli buyruqni tanlang:",
        reply_markup=get_anime_menu_keyboard()
    )

# 1. Nomi orqali izlash
async def search_by_name_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Аниме аты бойынша іздеуді бастайды."""
    await update.message.reply_text("Izlash uchun anime nomini yozing:", reply_markup=get_back_keyboard())
    return SEARCH_BY_NAME

async def search_by_name_receive(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Пайдаланушы енгізген аниме атын өңдейді."""
    anime_name = update.message.text.lower()
    found_anime = None
    for anime in ANIME_DB.values():
        if anime_name in anime['name'].lower():
            found_anime = anime
            break
    
    if found_anime:
        response = (
            f"✅ Topildi!\n\n"
            f"🎬 Nomi: {found_anime['name']}\n"
            f"🔢 Kodi: {found_anime['code']}\n"
            f"📄 Tavsif: {found_anime['description']}"
        )
        await update.message.reply_text(response, reply_markup=get_anime_menu_keyboard())
    else:
        await update.message.reply_text("❌ Afsus, bunday nomdagi anime topilmadi.", reply_markup=get_anime_menu_keyboard())
        
    return ConversationHandler.END

# 2. Kod orqali izlash
async def search_by_code_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Аниме коды бойынша іздеуді бастайды."""
    await update.message.reply_text("Izlash uchun anime kodini yozing (Masalan: A001):", reply_markup=get_back_keyboard())
    return SEARCH_BY_CODE

async def search_by_code_receive(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Пайдаланушы енгізген кодты өңдейді."""
    anime_code = update.message.text.upper()
    found_anime = None
    for anime in ANIME_DB.values():
        if anime_code == anime['code']:
            found_anime = anime
            break
            
    if found_anime:
        response = (
            f"✅ Topildi!\n\n"
            f"🎬 Nomi: {found_anime['name']}\n"
            f"🔢 Kodi: {found_anime['code']}\n"
            f"📄 Tavsif: {found_anime['description']}"
        )
        await update.message.reply_text(response, reply_markup=get_anime_menu_keyboard())
    else:
        await update.message.reply_text("❌ Afsus, bunday kodli anime topilmadi.", reply_markup=get_anime_menu_keyboard())

    return ConversationHandler.END

# 3. Barcha animelar
async def all_animes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Барлық анимелер тізімін көрсетеді (тек VIP және Admin үшін)."""
    user_id = update.effective_user.id
    role = get_user_role(user_id)

    if role in ["admin", "vip"]:
        if role == "admin":
            await update.message.reply_text("Xush kelibsiz Admin. Barcha animelar ro'yxati:")
        else: # vip
            await update.message.reply_text("Xush kelibsiz VIP a'zo. Barcha animelar ro'yxati:")
        
        anime_list = ""
        for i, anime in enumerate(ANIME_DB.values(), 1):
            anime_list += f"{i}. {anime['name']} (Kodi: {anime['code']})\n"
            
        if not anime_list:
            anime_list = "Hozircha animelar mavjud emas."
            
        await update.message.reply_text(anime_list)
    else:
        await update.message.reply_text("Bu bo'lim faqat VIP a'zo yoki Adminlar uchun.")

# 4. Ko'p ko'rilgan 20 anime
async def top_20_animes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Ең көп көрілген 20 анимені көрсетеді (тек VIP және Admin үшін)."""
    user_id = update.effective_user.id
    role = get_user_role(user_id)

    if role in ["admin", "vip"]:
        # Анимелерді көрілу саны бойынша сұрыптау
        sorted_animes = sorted(ANIME_DB.values(), key=lambda x: x['views'], reverse=True)
        top_animes = sorted_animes[:20]

        response = "📊 Eng ko'p ko'rilgan 20 ta anime:\n\n"
        for i, anime in enumerate(top_animes, 1):
            response += f"{i}. {anime['name']} - {anime['views']} marta ko'rilgan\n"

        await update.message.reply_text(response)
    else:
        await update.message.reply_text("Bu bo'lim faqat VIP a'zo yoki Adminlar uchun.")

# 5. Admin orqali izlash
async def search_via_admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Админ арқылы іздеуді бастайды (тек VIP және Admin үшін)."""
    user_id = update.effective_user.id
    role = get_user_role(user_id)

    if role in ["admin", "vip"]:
        if role == "admin":
            await update.message.reply_text("Admin, o'zingizga kerakli anime haqida yozishingiz mumkin:")
        else: # vip
            await update.message.reply_text("O'zingizga kerakli bo'lgan anime nomi yoki qisqacha tavsifini yozing:", reply_markup=get_back_keyboard())
        return SEARCH_VIA_ADMIN
    else:
        await update.message.reply_text("Bu bo'lim faqat VIP a'zo yoki Adminlar uchun.")
        return ConversationHandler.END

async def search_via_admin_receive(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Пайдаланушының сұранысын админдерге жібереді."""
    user = update.effective_user
    request_text = update.message.text
    
    # Админдерге хабарлама жіберу
    message_to_admin = (
        f"📢 Yangi anime so'rovi!\n\n"
        f"👤 Foydalanuvchi: {user.mention_html()} (ID: {user.id})\n"
        f"📝 So'rov: {request_text}"
    )
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(chat_id=admin_id, text=message_to_admin, parse_mode='HTML')
        except Exception as e:
            logger.error(f"Adminga ({admin_id}) xabar yuborishda xatolik: {e}")
            
    await update.message.reply_text("✅ Sizning so'rovingiz adminga yuborildi. Tez orada javob berishadi.", reply_markup=get_anime_menu_keyboard())
    return ConversationHandler.END


# --- 'Reklama' менюінің хендлерлері ---

async def reklama_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """'Reklama' менюін көрсетеді."""
    await update.message.reply_text(
        "Reklama bo'limi. Kerakli xizmatni tanlang:",
        reply_markup=get_reklama_menu_keyboard()
    )

# 1. Reklama olish
async def get_reklama_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Жарнама алу сұранысын бастайды."""
    text = (
        "Reklama narxlarini ko'rish uchun @anilordtvrek kanaliga o'ting.\n\n"
        "Reklama olmoqchi bo'lsangiz, quyidagilarni yozib yuboring:\n"
        "- Kanalga obuna kerakmi?\n"
        "- Qancha vaqtga kerak?\n\n"
        "Batafsil ma'lumotni yozib, shu yerga yuboring:"
    )
    await update.message.reply_text(text, reply_markup=get_back_keyboard())
    return GET_REKLAMA

async def get_reklama_receive(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Жарнама сұранысын админдерге жібереді."""
    user = update.effective_user
    reklama_request = update.message.text
    
    message_to_admin = (
        f"💸 Yangi reklama so'rovi!\n\n"
        f"👤 Foydalanuvchi: {user.mention_html()} (ID: {user.id})\n"
        f"📝 Xabar: {reklama_request}"
    )
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(chat_id=admin_id, text=message_to_admin, parse_mode='HTML')
        except Exception as e:
            logger.error(f"Adminga ({admin_id}) reklama xabarini yuborishda xatolik: {e}")

    await update.message.reply_text("✅ Xabaringiz adminga yuborildi. Sizga albatta javob berishadi.", reply_markup=get_reklama_menu_keyboard())
    return ConversationHandler.END

# 2. Reklama taklif qilish
async def suggest_reklama_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Жарнама ұсынысын бастайды."""
    await update.message.reply_text("O'zingizning taklifingizni yozing. Xabar adminga boradi:", reply_markup=get_back_keyboard())
    return SUGGEST_REKLAMA

async def suggest_reklama_receive(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Жарнама ұсынысын админдерге жібереді."""
    user = update.effective_user
    suggestion = update.message.text

    message_to_admin = (
        f"💡 Yangi reklama taklifi!\n\n"
        f"👤 Foydalanuvchi: {user.mention_html()} (ID: {user.id})\n"
        f"📝 Taklif: {suggestion}"
    )
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(chat_id=admin_id, text=message_to_admin, parse_mode='HTML')
        except Exception as e:
            logger.error(f"Adminga ({admin_id}) taklif xabarini yuborishda xatolik: {e}")
            
    await update.message.reply_text("✅ Taklifingiz uchun rahmat! Xabaringiz adminga yuborildi.", reply_markup=get_reklama_menu_keyboard())
    return ConversationHandler.END


# --- 'VIP' менюінің хендлерлері ---

async def vip_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """'VIP' менюін көрсетеді."""
    await update.message.reply_text(
        "VIP bo'limi haqida ma'lumot oling.",
        reply_markup=get_vip_menu_keyboard()
    )

async def vip_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """VIP артықшылықтары туралы ақпаратты көрсетеді."""
    info_text = (
        "👑 VIP A'zolikning afzalliklari:\n\n"
        "1. VIP a'zolar uchun yaratilgan maxsus komandalarga kirish mumkin.\n"
        "2. Ular uchun maxsus reaksiya (reaction) beriladi.\n"
        "3. 1 oy hech qanday kanalga obuna bo'lmasdan anime tomosha qilish mumkin.\n"
        "4. Agar botni o'chirmasangiz, yangi anime yuklanganda birinchi sizga jo'natiladi."
    )
    await update.message.reply_text(info_text)


# --- 'Support' менюінің хендлерлері ---

async def support_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Қолдау қызметіне хабарлама жазуды бастайды."""
    text = (
        "Agar jiddiy savol yoki yordam kerak bo'lsa-gina yozing.\n\n"
        "Qanday yordam kerakligini yozing:"
    )
    await update.message.reply_text(text, reply_markup=get_back_keyboard())
    return WAITING_SUPPORT_MESSAGE

async def support_receive(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Қолдау сұранысын админдерге жібереді."""
    user = update.effective_user
    support_message = update.message.text
    
    message_to_admin = (
        f"🆘 Yordam so'rovi (Support)!\n\n"
        f"👤 Foydalanuvchi: {user.mention_html()} (ID: {user.id})\n"
        f"📝 Murojaat: {support_message}"
    )
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(chat_id=admin_id, text=message_to_admin, parse_mode='HTML')
        except Exception as e:
            logger.error(f"Adminga ({admin_id}) support xabarini yuborishda xatolik: {e}")
            
    response_to_user = (
        "✅ Xabaringiz yuborildi. Adminlar tez orada ko'rib chiqishadi.\n\n"
        "⚠️ Eslatma: Agar xabaringiz jiddiy bo'lmasa, botdan ban yoki mute qilinishingiz mumkin."
    )
    await update.message.reply_text(response_to_user, reply_markup=get_main_menu_keyboard(user.id))
    return ConversationHandler.END


# --- 'Admin Panel' хендлері ---

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Админ панеліне кіруді өңдейді (уақытша)."""
    user_id = update.effective_user.id
    if get_user_role(user_id) == 'admin':
        await update.message.reply_text(
            "Admin paneliga xush kelibsiz! Bu yerda botni boshqarish funksiyalari bo'ladi.",
            # Болашақта админге арналған арнайы батырмалар қосылады
            reply_markup=get_main_menu_keyboard(user_id) 
        )
    else:
        # Бұл хабарлама көрсетілмеуі керек, себебі батырма тек админдерде бар
        await update.message.reply_text("Sizda bu bo'limga kirish huquqi yo'q.")


def main() -> None:
    """Ботты іске қосады және барлық хендлерлерді тіркейді."""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN topilmadi! .env faylini tekshiring.")
        return

    application = Application.builder().token(BOT_TOKEN).build()

    # --- Аниме іздеуге арналған ConversationHandler ---
    anime_search_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^Nomi orqali izlash$"), search_by_name_start),
            MessageHandler(filters.Regex("^Kod orqali izlash$"), search_by_code_start),
            MessageHandler(filters.Regex("^Admin orqali izlash$"), search_via_admin_start),
        ],
        states={
            SEARCH_BY_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, search_by_name_receive)],
            SEARCH_BY_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, search_by_code_receive)],
            SEARCH_VIA_ADMIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, search_via_admin_receive)],
        },
        fallbacks=[MessageHandler(filters.Regex("^Orqaga$"), back_to_main_menu)],
    )

    # --- Рекламаға арналған ConversationHandler ---
    reklama_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^Reklama olish$"), get_reklama_start),
            MessageHandler(filters.Regex("^Reklama taklif qilish$"), suggest_reklama_start),
        ],
        states={
            GET_REKLAMA: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_reklama_receive)],
            SUGGEST_REKLAMA: [MessageHandler(filters.TEXT & ~filters.COMMAND, suggest_reklama_receive)],
        },
        fallbacks=[MessageHandler(filters.Regex("^Orqaga$"), back_to_main_menu)],
    )

    # --- Қолдау қызметіне арналған ConversationHandler ---
    support_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Support$"), support_start)],
        states={
            WAITING_SUPPORT_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, support_receive)]
        },
        fallbacks=[MessageHandler(filters.Regex("^Orqaga$"), back_to_main_menu)],
    )


    # --- Барлық хендлерлерді тіркеу ---
    application.add_handler(CommandHandler("start", start))

    # Негізгі меню батырмалары
    application.add_handler(MessageHandler(filters.Regex("^Anime Izlash$"), anime_menu))
    application.add_handler(MessageHandler(filters.Regex("^Reklama$"), reklama_menu))
    application.add_handler(MessageHandler(filters.Regex("^VIP$"), vip_menu))
    application.add_handler(MessageHandler(filters.Regex("^ADMIN PANELIGA O'TISH$"), admin_panel))
    
    # Аниме менюінің ішкі батырмалары
    application.add_handler(MessageHandler(filters.Regex("^Barcha animelar$"), all_animes))
    application.add_handler(MessageHandler(filters.Regex("^Ko'p ko'rilgan 20 anime$"), top_20_animes))
    
    # VIP менюінің ішкі батырмасы
    application.add_handler(MessageHandler(filters.Regex("^VIPda nimalar bor\?$"), vip_info))

    # Conversation Handler-лерді қосу
    application.add_handler(anime_search_conv)
    application.add_handler(reklama_conv)
    application.add_handler(support_conv)
    
    # "Orqaga" батырмасын глобалды түрде өңдеу (егер диалог ішінде болмаса)
    application.add_handler(MessageHandler(filters.Regex("^Orqaga$"), back_to_main_menu))
    
    # Ботты іске қосу
    application.run_polling()


if __name__ == "__main__":
    main()
