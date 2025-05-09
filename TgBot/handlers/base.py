from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from libs.keyboards import get_main_menu
from libs.logger import get_logger

logger = get_logger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    logger.info(f"User {user.id} started interaction")
    try:
        await update.message.reply_text(
            "Добро пожаловать в систему путевых листов! Нажмите 'Начать маршрут' для работы.",
            reply_markup=get_main_menu()
        )
        return ConversationHandler.END  # Возвращаем END, так как сценарий начинается по кнопке
    except Exception as e:
        logger.error(f"Start command error for user {user.id}: {e}")
        await update.message.reply_text("Произошла ошибка. Пожалуйста, попробуйте позже.")
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    logger.info(f"User {user.id} canceled operation")
    try:
        await update.message.reply_text(
            "Действие отменено. Для начала нового маршрута нажмите /start",
            reply_markup=get_main_menu()
        )
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Cancel command error for user {user.id}: {e}")
        return ConversationHandler.END