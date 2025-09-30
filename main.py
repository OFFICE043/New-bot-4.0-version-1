# main.py
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import BOT_TOKEN
from database.db_manager import init_db

# Handlers
from handlers.start import start
from handlers.user.common_handlers import back_to_main_menu
from handlers.user.anime_search import to_anime_search_menu, anime_search_conv_handler, all_animes, top_animes, search_via_admin
from handlers.user.reklama import to_reklama_menu, reklama_conv_handler
from handlers.user.support_vip import vip_info, support_conv_handler

def main() -> None:
    init_db()
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    application = Application.builder().token(BOT_TOKEN).build()

    # --- USER PANEL HANDLERS ---
    user_handlers = [
        MessageHandler(filters.Regex("^🎬 Anime Izlash$"), to_anime_search_menu),
        MessageHandler(filters.Regex("^📢 Reklama$"), to_reklama_menu),
        MessageHandler(filters.Regex("^👑 VIP$"), vip_info),
        MessageHandler(filters.Regex("^📚 Barcha animelar$"), all_animes),
        MessageHandler(filters.Regex("^🏆 Ko'p ko'rilgan 20 anime$"), top_animes),
        MessageHandler(filters.Regex("^🧑‍💻 Admin orquali izlash$"), search_via_admin),
        MessageHandler(filters.Regex("^⬅️ Orqaga$"), back_to_main_menu),
        anime_search_conv_handler,
        reklama_conv_handler,
        support_conv_handler,
    ]
    application.add_handlers(user_handlers)
    
    # /start командасы (әрдайым соңында болғаны дұрыс)
    application.add_handler(CommandHandler("start", start))

    application.run_polling()

if __name__ == "__main__":
    main()
