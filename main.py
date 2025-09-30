# main.py
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from config import BOT_TOKEN
from database.db_manager import init_db

# НЕГІЗГІ ХЕНДЛЕРЛЕР
from handlers.start import start

# USER PANEL ХЕНДЛЕРЛЕРІ
from handlers.user.anime_search import anime_search_conv_handler, to_anime_search_menu, back_to_main_menu, all_animes, top_animes
from handlers.user.reklama import reklama_conv_handler, to_reklama_menu
from handlers.user.support_vip import vip_info, support_conv_handler, to_support_menu

# ADMIN PANEL ХЕНДЛЕРЛЕРІ
from handlers.admin.panel_navigation import to_admin_panel, to_anime_panel, to_settings_panel, switch_to_user_panel
from handlers.admin.anime_management import anime_management_conv
from handlers.admin.settings_management import vip_settings_conv
from handlers.admin.broadcast import broadcast_conv
# ... және басқа админ хендлерлері

def main() -> None:
    init_db()
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
    application = Application.builder().token(BOT_TOKEN).build()

    # --- USER PANEL ---
    application.add_handler(MessageHandler(filters.Regex("^🎬 Anime Izlash$"), to_anime_search_menu))
    application.add_handler(MessageHandler(filters.Regex("^📢 Reklama$"), to_reklama_menu))
    application.add_handler(MessageHandler(filters.Regex("^👑 VIP$"), vip_info))
    application.add_handler(MessageHandler(filters.Regex("^📞 Support$"), to_support_menu))
    application.add_handler(MessageHandler(filters.Regex("^⬅️ Orqaga$"), back_to_main_menu))
    
    # User Conversation Handlers
    application.add_handler(anime_search_conv_handler)
    application.add_handler(reklama_conv_handler)
    application.add_handler(support_conv_handler)
    
    # --- ADMIN PANEL ---
    application.add_handler(MessageHandler(filters.Regex("^🎬 Anime Panel$"), to_anime_panel))
    application.add_handler(MessageHandler(filters.Regex("^⚙️ Sozlamalar Panel$"), to_settings_panel))
    application.add_handler(MessageHandler(filters.Regex("^👤 User Panelga o'tish$"), switch_to_user_panel))
    application.add_handler(MessageHandler(filters.Regex("^⬅️ Orqaga \(Admin Panel\)$"), to_admin_panel))

    # Admin Conversation Handlers
    application.add_handler(anime_management_conv)
    application.add_handler(vip_settings_conv)
    application.add_handler(broadcast_conv)

    # /start командасы (админ немесе юзер екенін анықтайды)
    application.add_handler(CommandHandler("start", start))

    # Ботты іске қосу
    application.run_polling()

if __name__ == "__main__":
    main()
