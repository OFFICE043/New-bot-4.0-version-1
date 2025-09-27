from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
import database
import keyboards as kb
from handlers import user_handlers
import asyncio

# States for admin conversations
class AdminStates:
    ADD_ANIME_CODE = 1
    ADD_ANIME_NAME = 2
    ADD_ANIME_DESC = 3
    DELETE_ANIME_CODE = 4
    ADD_ADMIN_ID = 5
    REMOVE_ADMIN_ID = 6
    BROADCAST_MESSAGE = 7

# === Main Navigation ===
async def admin_panel_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Admin paneliga xush kelibsiz!", reply_markup=kb.admin_panel_main_menu_keyboard)
    return ConversationHandler.END

async def back_to_user_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await user_handlers.start(update, context)
    return ConversationHandler.END

# === Anime Panel ===
async def anime_panel_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Anime paneli:", reply_markup=kb.anime_panel_menu_keyboard)

async def add_anime_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Yangi anime kodini kiriting:", reply_markup=kb.cancel_keyboard)
    return AdminStates.ADD_ANIME_CODE

async def add_anime_get_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['new_anime_code'] = update.message.text
    await update.message.reply_text("Endi anime nomini kiriting:")
    return AdminStates.ADD_ANIME_NAME

async def add_anime_get_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['new_anime_name'] = update.message.text
    await update.message.reply_text("Endi anime haqida qisqacha ma'lumot (ta'rif) kiriting:")
    return AdminStates.ADD_ANIME_DESC

async def add_anime_finish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    code = context.user_data['new_anime_code']
    name = context.user_data['new_anime_name']
    desc = update.message.text
    database.add_anime(code, name, desc)
    await update.message.reply_text(f"✅ Anime '{name}' (kodi: {code}) bazaga muvaffaqiyatli qo'shildi!")
    context.user_data.clear()
    return await admin_panel_start(update, context)

async def delete_anime_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("O'chirmoqchi bo'lgan anime kodini kiriting:", reply_markup=kb.cancel_keyboard)
    return AdminStates.DELETE_ANIME_CODE

async def delete_anime_finish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    code = update.message.text
    anime = database.get_anime_by_code(code)
    if anime:
        database.delete_anime(code)
        await update.message.reply_text(f"✅ Anime '{anime[2]}' (kodi: {code}) bazadan o'chirildi.")
    else:
        await update.message.reply_text("❌ Bunday kodli anime topilmadi.")
    return await admin_panel_start(update, context)

async def list_anime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    animes = database.get_all_anime()
    if not animes:
        await update.message.reply_text("Hozircha bazada animelar mavjud emas.")
    else:
        response = "📄 Barcha animelar ro'yxati:\n\n"
        response += "\n".join([f"<code>{code}</code> - {name}" for code, name in animes])
        await update.message.reply_html(response)

async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users_count = database.get_users_count()
    anime_count = database.get_anime_count()
    await update.message.reply_html(f"<b>📊 Bot statistikasi:</b>\n\n👥 Foydalanuvchilar soni: {users_count}\n🎬 Animelar soni: {anime_count}")

# === Admin Management ===
async def manage_admins_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Adminlarni boshqarish paneli:", reply_markup=kb.manage_admins_menu_keyboard)

async def add_admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Qo'shmoqchi bo'lgan adminning Telegram ID raqamini kiriting:", reply_markup=kb.cancel_keyboard)
    return AdminStates.ADD_ADMIN_ID

async def add_admin_finish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        admin_id = int(update.message.text)
        database.add_admin(admin_id)
        await update.message.reply_text(f"✅ Admin <code>{admin_id}</code> muvaffaqiyatli qo'shildi.")
    except ValueError:
        await update.message.reply_text("❌ ID faqat raqamlardan iborat bo'lishi kerak.")
    return await admin_panel_start(update, context)

async def remove_admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("O'chirmoqchi bo'lgan adminning Telegram ID raqamini kiriting:", reply_markup=kb.cancel_keyboard)
    return AdminStates.REMOVE_ADMIN_ID

async def remove_admin_finish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        admin_id = int(update.message.text)
        if admin_id in context.bot_data.get('head_admins', []):
            await update.message.reply_text("❌ Bosh adminni o'chirib bo'lmaydi.")
        else:
            database.remove_admin(admin_id)
            await update.message.reply_text(f"✅ Admin <code>{admin_id}</code> muvaffaqiyatli o'chirildi.")
    except ValueError:
        await update.message.reply_text("❌ ID faqat raqamlardan iborat bo'lishi kerak.")
    return await admin_panel_start(update, context)

async def list_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admins = database.get_all_admins()
    response = "<b>📋 Barcha adminlar ro'yxati:</b>\n\n"
    for admin_id in admins:
        response += f"<code>{admin_id}</code>\n"
    await update.message.reply_html(response)
    
# === Broadcast ===
async def broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Barcha foydalanuvchilarga yuboriladigan xabarni kiriting (matn, rasm, video...):", reply_markup=kb.cancel_keyboard)
    return AdminStates.BROADCAST_MESSAGE

async def broadcast_finish(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    all_users = database.get_all_user_ids()
    success_count = 0
    fail_count = 0
    await update.message.reply_text(f"Xabar yuborish boshlandi. Jami foydalanuvchilar: {len(all_users)}. Bu biroz vaqt olishi mumkin.")
    
    for user_id in all_users:
        try:
            await context.bot.copy_message(chat_id=user_id, from_chat_id=update.message.chat_id, message_id=update.message.message_id)
            success_count += 1
            await asyncio.sleep(0.1) # Flood control
        except Exception:
            fail_count += 1
            
    await update.message.reply_text(f"✅ Xabar yuborish yakunlandi.\n\nMuvaffaqiyatli: {success_count}\nXatolik: {fail_count}")
    return await admin_panel_start(update, context)

# === Database Backup ===
async def get_db_backup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.send_document(chat_id=update.effective_chat.id, document=open(database.DB_NAME, 'rb'))
    except FileNotFoundError:
        await update.message.reply_text("❌ Baza fayli topilmadi.")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text("Amal bekor qilindi.")
    return await admin_panel_start(update, context)
