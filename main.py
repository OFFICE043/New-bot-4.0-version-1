import logging
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, ConversationHandler
)

from config import BOT_TOKEN, HEAD_ADMINS
from keep_alive import keep_alive
from database import init_db, get_all_admins
from handlers import user_handlers as uh
from handlers import admin_handlers as ah
import keyboards as kb

# Логгингті қосу
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Админдерді тексеретін арнайы фильтр
class AdminFilter(filters.BaseFilter):
    def filter(self, message: filters.Message) -> bool:
        # get_all_admins() функциясы Бас админдерді де, қарапайым админдерді де қайтарады
        return message.from_user.id in get_all_admins()

admin_filter = AdminFilter()

def main() -> None:
    """Ботты іске қосатын негізгі функция"""
    keep_alive()
    init_db()

    application = Application.builder().token(BOT_TOKEN).build()
    
    # --- Conversation Handlers (Күрделі, көп қадамды диалогтар үшін) ---

    # 1. User панелінің диалогтары
    user_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.TEXT & filters.Regex(f'^{kb.BTN_SEARCH_BY_NAME}$'), uh.search_by_name_start),
            MessageHandler(filters.TEXT & filters.Regex(f'^{kb.BTN_SEARCH_BY_CODE}$'), uh.search_by_code_start),
            MessageHandler(filters.TEXT & filters.Regex(f'^{kb.BTN_SUPPORT}$'), uh.support_start),
        ],
        states={
            uh.UserStates.ANIME_SEARCH_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, uh.process_name_search)],
            uh.UserStates.ANIME_SEARCH_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, uh.process_code_search)],
            uh.UserStates.SUPPORT_TICKET: [MessageHandler(filters.TEXT & ~filters.COMMAND, uh.process_support_ticket)],
        },
        fallbacks=[MessageHandler(filters.TEXT & filters.Regex(f'^{kb.BTN_ORQAGA}$'), uh.cancel_conversation)],
    )
    application.add_handler(user_conv)
    
    # 2. Admin панелінің диалогтары
    admin_conv = ConversationHandler(
        entry_points=[
            MessageHandler(admin_filter & filters.TEXT & filters.Regex(f'^{kb.BTN_ADD_ANIME}$'), ah.add_anime_start),
            MessageHandler(admin_filter & filters.TEXT & filters.Regex(f'^{kb.BTN_DELETE_ANIME}$'), ah.delete_anime_start),
            MessageHandler(admin_filter & filters.TEXT & filters.Regex(f'^{kb.BTN_ADD_ADMIN}$'), ah.add_admin_start),
            MessageHandler(admin_filter & filters.TEXT & filters.Regex(f'^{kb.BTN_REMOVE_ADMIN}$'), ah.remove_admin_start),
            MessageHandler(admin_filter & filters.TEXT & filters.Regex(f'^{kb.BTN_BROADCAST}$'), ah.broadcast_start),
        ],
        states={
            ah.AdminStates.ADD_ANIME_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ah.add_anime_get_code)],
            ah.AdminStates.ADD_ANIME_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ah.add_anime_get_name)],
            ah.AdminStates.ADD_ANIME_DESC: [MessageHandler(filters.TEXT & ~filters.COMMAND, ah.add_anime_finish)],
            ah.AdminStates.DELETE_ANIME_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ah.delete_anime_finish)],
            ah.AdminStates.ADD_ADMIN_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, ah.add_admin_finish)],
            ah.AdminStates.REMOVE_ADMIN_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, ah.remove_admin_finish)],
            ah.AdminStates.BROADCAST_MESSAGE: [MessageHandler(filters.ALL & ~filters.COMMAND, ah.broadcast_finish)],
        },
        fallbacks=[MessageHandler(admin_filter & filters.TEXT & filters.Regex(f'^{kb.BTN_CANCEL}$'), ah.cancel)],
    )
    application.add_handler(admin_conv)

    # --- Simple Message Handlers (Қарапайым, бір реттік командалар) ---
    
    # User handlers
    application.add_handler(CommandHandler("start", uh.start))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(f'^{kb.BTN_ANIME_SEARCH}$'), uh.anime_search_menu))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(f'^{kb.BTN_ALL_ANIME}$'), uh.show_all_anime))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(f'^{kb.BTN_REKLAMA}$'), uh.reklama_menu))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(f'^{kb.BTN_VIP}$'), uh.vip_menu))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(f'^{kb.BTN_VIP_INFO}$'), uh.vip_info))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(f'^{kb.BTN_ORQAGA}$'), uh.start)) # Негізгі менюге оралу

    # Admin handlers (protected by AdminFilter)
    application.add_handler(MessageHandler(admin_filter & filters.TEXT & filters.Regex(f'^{kb.BTN_TO_ADMIN_PANEL}$'), ah.admin_panel_start))
    application.add_handler(MessageHandler(admin_filter & filters.TEXT & filters.Regex(f'^{kb.BTN_TO_USER_PANEL}$'), ah.back_to_user_panel))
    application.add_handler(MessageHandler(admin_filter & filters.TEXT & filters.Regex(f'^{kb.BTN_ANIME_PANEL}$'), ah.anime_panel_menu))
    application.add_handler(MessageHandler(admin_filter & filters.TEXT & filters.Regex(f'^{kb.BTN_LIST_ANIME}$'), ah.list_anime))
    application.add_handler(MessageHandler(admin_filter & filters.TEXT & filters.Regex(f'^{kb.BTN_STATS}$'), ah.show_stats))
    application.add_handler(MessageHandler(admin_filter & filters.TEXT & filters.Regex(f'^{kb.BTN_MANAGE_ADMINS}$'), ah.manage_admins_menu))
    application.add_handler(MessageHandler(admin_filter & filters.TEXT & filters.Regex(f'^{kb.BTN_LIST_ADMINS}$'), ah.list_admins))
    application.add_handler(MessageHandler(admin_filter & filters.TEXT & filters.Regex(f'^{kb.BTN_GET_DB}$'), ah.get_db_backup))
    application.add_handler(MessageHandler(admin_filter & filters.TEXT & filters.Regex(f'^{kb.BTN_BACK_TO_ADMIN_PANEL}$'), ah.admin_panel_start))
    
    logger.info("Бот іске қосылуда...")
    application.run_polling()


if __name__ == "__main__":
    main()

