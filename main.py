# main.py
# ... (бұрынғы импорттар)
from handlers.start import start
from handlers.user.anime_search import to_anime_search_menu, back_to_main_menu, anime_search_conv_handler, all_animes, top_animes
from handlers.user.reklama import to_reklama_menu, reklama_conv_handler
from handlers.user.support_vip import vip_info

def main() -> None:
    init_db()
    # ...
    application = Application.builder().token(BOT_TOKEN).build()

    # User Panel Handlers
    application.add_handler(MessageHandler(filters.Regex("^🎬 Anime Izlash$"), to_anime_search_menu))
    application.add_handler(MessageHandler(filters.Regex("^📢 Reklama$"), to_reklama_menu))
    application.add_handler(MessageHandler(filters.Regex("^👑 VIP$"), vip_info))

    application.add_handler(anime_search_conv_handler)
    application.add_handler(reklama_conv_handler)
    
    application.add_handler(MessageHandler(filters.Regex("^📚 Barcha animelar$"), all_animes))
    application.add_handler(MessageHandler(filters.Regex("^🏆 Ko'p ko'rilgan 20 anime$"), top_animes))
    
    application.add_handler(MessageHandler(filters.Regex("^⬅️ Orqaga$"), back_to_main_menu))
    application.add_handler(CommandHandler("start", start))
    
    application.run_polling()

if __name__ == "__main__":
    main()
