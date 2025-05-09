from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

import sys
sys.path.append('.')
from libs.keyboards import get_main_menu

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Добро пожаловать в систему путевых листов!",
        reply_markup=get_main_menu()
    )
    return 0  # START state

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Действие отменено. Для начала нового маршрута нажмите /start",
        reply_markup=get_main_menu()
    )
    return ConversationHandler.END