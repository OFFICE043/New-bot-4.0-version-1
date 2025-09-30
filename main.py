# main.py
import logging
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

# --- Конфигурация ---
# Токен мен әкімші ID-лерін бөлек файлдан импорттаймыз
from config import BOT_TOKEN, ADMIN_IDS

# --- Дерекқор (қажет болса) ---
# from database.db_manager import init_db

# --- Пайдаланушы Хендлерлері (User Handlers) ---
# Пайдаланушыға қатысты барлық функциялар осы файлдардан импортталады
from handlers.start import start
from handlers.user.common_handlers import back_to_main_menu
from handlers.user.anime_search import (
    to_anime_search_menu,
    anime_search_conv_handler,
    all_animes,
    top_animes,
    search_via_admin,
)
from handlers.user.reklama import to_reklama_menu, reklama_conv_handler
from handlers.user.support_vip import vip_info, support_conv_handler

# --- Әкімші Хендлерлері (Admin Handlers) ---
# Әкімшіге қатысты барлық функциялар осы файлдардан импортталады
from handlers.admin_handlers import (
    admin_panel,
    show_stats,
    broadcast_conv_handler,
    exit_admin_panel,
)

# Әкімшілерді анықтайтын арнайы фильтр
# Бұл фильтрді пайдаланып, командаларды тек ADMIN_IDS тізіміндегілерге ғана қолжетімді етеміз
admin_filter = filters.User(user_id=ADMIN_IDS)

def main() -> None:
    """Ботты іске қосатын және барлық хендлерлерді тіркейтін негізгі функция"""
    # init_db()  # Дерекқорды инициализациялау (қажет болса)

    # Логтауды конфигурациялау
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)

    # Бот экземплярын (Application) құру
    application = Application.builder().token(BOT_TOKEN).build()

    # =================================================================
    # --- ADMIN PANEL HANDLERS (ӘКІМШІ ПАНЕЛІНІҢ ӨҢДЕУШІЛЕРІ) ---
    # =================================================================
    # Бұл хендлерлер тек `admin_filter`-ден өткен, яғни ADMIN_IDS тізіміндегі
    # пайдаланушылар үшін ғана іске қосылады.
    admin_handlers_group = [
        # /admin командасы әкімші панелін ашады
        CommandHandler("admin", admin_panel, filters=admin_filter),

        # Әкімші панелінің ішіндегі батырмаларды өңдеу
        MessageHandler(filters.Regex("^📊 Статистика$") & admin_filter, show_stats),
        MessageHandler(filters.Regex("^⬅️ Негізгі мәзірге оралу$") & admin_filter, exit_admin_panel),

        # Хабарлама жіберуге арналған ConversationHandler
        broadcast_conv_handler,
    ]
    application.add_handlers(admin_handlers_group)

    # =================================================================
    # --- USER PANEL HANDLERS (ПАЙДАЛАНУШЫ ПАНЕЛІНІҢ ӨҢДЕУШІЛЕРІ) ---
    # =================================================================
    # Бұл хендлерлер барлық пайдаланушылар үшін жұмыс істейді.
    user_handlers_group = [
        # Негізгі мәзір батырмалары
        MessageHandler(filters.Regex("^🎬 Anime Izlash$"), to_anime_search_menu),
        MessageHandler(filters.Regex("^📢 Reklama$"), to_reklama_menu),
        MessageHandler(filters.Regex("^👑 VIP$"), vip_info),

        # Аниме іздеу мәзірінің батырмалары
        MessageHandler(filters.Regex("^📚 Barcha animelar$"), all_animes),
        MessageHandler(filters.Regex("^🏆 Ko'p ko'rilgan 20 anime$"), top_animes),
        MessageHandler(filters.Regex("^🧑‍💻 Admin orquali izlash$"), search_via_admin),

        # Жалпы батырмалар
        MessageHandler(filters.Regex("^⬅️ Orqaga$"), back_to_main_menu),

        # Пайдаланушыға арналған ConversationHandler-лер
        anime_search_conv_handler,
        reklama_conv_handler,
        support_conv_handler,
    ]
    application.add_handlers(user_handlers_group)

    # =================================================================
    # --- ЖАЛПЫ КОМАНДАЛАР ---
    # =================================================================
    # /start командасы барлық пайдаланушыларға ортақ және ең соңында тіркелгені дұрыс.
    application.add_handler(CommandHandler("start", start))

    # Ботты іске қосу
    print("Бот іске қосылды...")
    application.run_polling()

if __name__ == "__main__":
    main()

