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

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom filter for checking if a user is an admin
class AdminFilter(filters.BaseFilter):
    def filter(self, message: filters.Message) -> bool:
        return message.from_user.id in get_all_admins()

def main() -> None:
    keep_alive()
    init_db()

    application = Application.builder().token(BOT_TOKEN).build()
    application.bot_data['head_admins'] = HEAD_ADMINS

    # --- USER PANEL CONVERSATION HANDLER ---
    user_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.TEXT & filters.Regex(f'^{kb.BTN_SEARCH_BY_NAME}$'), uh.search_by_name_start),
            MessageHandler(filters.TEXT & filters.Regex(f'^{kb.BTN_SEARCH_BY_CODE}$'), uh.search_by_code_start),
            MessageHandler(filters.TEXT & filters.Regex(f'^{kb.BTN_SUPPORT}$'), uh.support_start),
        ],
        states={
            uh.States.ANIME_SEARCH_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, uh.process_name_search)],
            uh.States.ANIME_SEARCH_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, uh.process_code_search)],
            uh.States.SUPPORT_TICKET: [MessageHandler(filters.TEXT & ~filters.COMMAND, uh.process_support_ticket)],
        },
        fallbacks=[MessageHandler(filters.TEXT & (filters.Regex(f'^{kb.BTN_CANCEL}$') | filters.Regex(f'^{kb.BTN_BACK_TO_MAIN}$')), uh.start)],
    )
    application.add_handler(user_conv)
    
    # --- ADMIN PANEL CONVERSATION HANDLER ---
    admin_conv = ConversationHandler(
        entry_points=[
            MessageHandler(AdminFilter() & filters.TEXT & filters.Regex(f'^{kb.BTN_ADD_ANIME}$'), ah.add_anime_start),
            MessageHandler(AdminFilter() & filters.TEXT & filters.Regex(f'^{kb.BTN_DELETE_ANIME}$'), ah.delete_anime_start),
            MessageHandler(AdminFilter() & filters.TEXT & filters.Regex(f'^{kb.BTN_ADD_ADMIN}$'), ah.add_admin_start),
            MessageHandler(AdminFilter() & filters.TEXT & filters.Regex(f'^{kb.BTN_REMOVE_ADMIN}$'), ah.remove_admin_start),
            MessageHandler(AdminFilter() & filters.TEXT & filters.Regex(f'^{kb.BTN_BROADCAST}$'), ah.broadcast_start),
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
        fallbacks=[MessageHandler(filters.TEXT & filters.Regex(f'^{kb.BTN_CANCEL}$'), ah.cancel)],
    )
    application.add_handler(admin_conv)

    # --- SIMPLE HANDLERS (NO CONVERSATION) ---
    # User handlers
    application.add_handler(CommandHandler("start", uh.start))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(f'^{kb.BTN_ANIME_SEARCH}$'), uh.anime_search_menu))
    # ... (other simple user handlers) ...

    # Admin handlers
    application.add_handler(MessageHandler(AdminFilter() & filters.TEXT & filters.Regex(f'^{kb.BTN_TO_ADMIN_PANEL}$'), ah.admin_panel_start))
    application.add_handler(MessageHandler(AdminFilter() & filters.TEXT & filters.Regex(f'^{kb.BTN_TO_USER_PANEL}$'), ah.back_to_user_panel))
    application.add_handler(MessageHandler(AdminFilter() & filters.TEXT & filters.Regex(f'^{kb.BTN_ANIME_PANEL}$'), ah.anime_panel_menu))
    application.add_handler(MessageHandler(AdminFilter() & filters.TEXT & filters.Regex(f'^{kb.BTN_LIST_ANIME}$'), ah.list_anime))
    application.add_handler(MessageHandler(AdminFilter() & filters.TEXT & filters.Regex(f'^{kb.BTN_STATS}$'), ah.show_stats))
    application.add_handler(MessageHandler(AdminFilter() & filters.TEXT & filters.Regex(f'^{kb.BTN_MANAGE_ADMINS}$'), ah.manage_admins_menu))
    application.add_handler(MessageHandler(AdminFilter() & filters.TEXT & filters.Regex(f'^{kb.BTN_LIST_ADMINS}$'), ah.list_admins))
    application.add_handler(MessageHandler(AdminFilter() & filters.TEXT & filters.Regex(f'^{kb.BTN_GET_DB}$'), ah.get_db_backup))
    application.add_handler(MessageHandler(AdminFilter() & filters.TEXT & filters.Regex(f'^{kb.BTN_BACK_TO_MAIN_ADMIN_PANEL}$'), ah.admin_panel_start))

    logger.info("Бот іске қосылуда...")
    application.run_polling()

if __name__ == "__main__":
    main()
