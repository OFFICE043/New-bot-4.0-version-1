import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from config import BOT_TOKEN
from keep_alive import keep_alive

# Логгингті (жұмыс журналын) қосу
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """/start командасына уақытша жауап"""
    user = update.effective_user
    await update.message.reply_html(
        f"Salom, {user.mention_html()}! Bot ishga tushdi. Yaqinda to'liq ishlaydi."
    )


def main() -> None:
    """Ботты іске қосатын негізгі функция"""
    # Render-дің ұйықтап қалмауы үшін веб-серверді іске қосу
    keep_alive()

    # Боттың негізін құру
    application = Application.builder().token(BOT_TOKEN).build()

    # Уақытша /start командасын тіркеу
    # Нағыз /start логикасын кейін user_handlers.py файлына жазамыз
    application.add_handler(CommandHandler("start", start))

    # БОЛАШАҚТА: user_handlers.py және admin_handlers.py-ден негізгі хэндлерлерді осында тіркейміз

    logger.info("Бот іске қосылуда...")
    
    # Ботты іске қосу (жаңа хабарламаларды тексеруді бастау)
    application.run_polling()


if __name__ == "__main__":
    main()
