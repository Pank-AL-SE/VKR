from telegram import Update
from telegram.ext import ContextTypes
from libs.keyboards import get_confirmation_keyboard, get_checkpoints_keyboard
from models.models import RouteData

async def start_route(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    route_info = """..."""  # Ваша информация о маршруте
    
    context.user_data['route'] = {
        'vehicle_info': route_info,
        'checkpoints': [...],  # Ваши точки маршрута
        'current_checkpoint': None
    }
    
    await update.message.reply_text(
        f"Информация о маршруте:\n{route_info}\n\nВсё верно?",
        reply_markup=get_confirmation_keyboard()
    )
    return 1  # CONFIRM_ROUTE state

async def confirm_route(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Путевой лист сформирован!")
    await send_checkpoints(update, context)
    return 2  # ON_ROUTE state

async def send_checkpoints(update: Update, context: ContextTypes.DEFAULT_TYPE):
    checkpoints = context.user_data['route']['checkpoints']
    await update.message.reply_text(
        "Текущие точки маршрута:",
        reply_markup=get_checkpoints_keyboard(checkpoints)
    )