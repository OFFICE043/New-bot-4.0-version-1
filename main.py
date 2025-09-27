import logging
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, ConversationHandler
)

from config import BOT_TOKEN
from keep_alive import keep_alive
from database import init_db
from handlers import user_handlers as uh
import keyboards as kb

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


def main() -> None:
    """Ботты іске қосатын негізгі функция"""
    keep_alive()
    init_db()

    application = Application.builder().token(BOT_TOKEN).build()

    # Диалогты (сөйлесуді) басқаратын негізгі хэндлер
    conv_handler = ConversationHandler(
        entry_points=[
            # Диалогты бастайтын батырмалар
            MessageHandler(filters.TEXT & filters.Regex(f'^{kb.BTN_SEARCH_BY_NAME}$'), uh.search_by_name_start),
            MessageHandler(filters.TEXT & filters.Regex(f'^{kb.BTN_SEARCH_BY_CODE}$'), uh.search_by_code_start),
            MessageHandler(filters.TEXT & filters.Regex(f'^{kb.BTN_SUPPORT}$'), uh.support_start),
        ],
        states={
            # Әр күйде бот қандай функцияны орындайтынын анықтаймыз
            uh.States.ANIME_SEARCH_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, uh.process_name_search)],
            uh.States.ANIME_SEARCH_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, uh.process_code_search)],
            uh.States.SUPPORT_TICKET: [MessageHandler(filters.TEXT & ~filters.COMMAND, uh.process_support_ticket)],
        },
        # Диалогты тоқтататын батырмалар
        fallbacks=[
            MessageHandler(filters.TEXT & filters.Regex(f'^{kb.BTN_CANCEL}$'), uh.start),
            MessageHandler(filters.TEXT & filters.Regex(f'^{kb.BTN_BACK_TO_MAIN}$'), uh.start)
        ],
    )
    
    application.add_handler(conv_handler)
    
    # Диалогсыз, бірден жауап беретін қарапайым командалар
    application.add_handler(CommandHandler("start", uh.start))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(f'^{kb.BTN_ANIME_SEARCH}$'), uh.anime_search_menu))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(f'^{kb.BTN_REKLAMA}$'), uh.reklama_menu))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(f'^{kb.BTN_VIP}$'), uh.vip_menu))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(f'^{kb.BTN_GET_AD}$'), uh.get_ad_info))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(f'^{kb.BTN_VIP_INFO}$'), uh.get_vip_info))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(f'^{kb.BTN_ALL_ANIME}$'), uh.show_all_anime))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(f'^{kb.BTN_TOP_20}$'), uh.show_top_20))
    # Негізгі менюге қайтатын батырманы бөлек тіркеу маңызды
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(f'^{kb.BTN_BACK_TO_MAIN}$'), uh.start))

    
    logger.info("Бот іске қосылуда...")
    application.run_polling()


if __name__ == "__main__":
    main()
