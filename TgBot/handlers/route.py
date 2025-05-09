from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, CallbackQueryHandler, ConversationHandler
from libs.keyboards import get_confirmation_keyboard, get_main_menu
from libs.logger import get_logger

logger = get_logger(__name__)

async def start_route(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    logger.info(f"User {user.id} starting new route")
    
    try:
        route_info = """🚗 Автомобиль: А123БВ777
🟢 Статус: Исправен
⛽ Топливо: ~45 литров
📊 Одометр: 125 643 км
❗ Примечания: Правый поворотник мигает быстрее

📍 Точки маршрута:
1. Склад №1 (ул. Ленина, 10) - загрузка
2. Магазин "Продукты" (ул. Мира, 5) - выгрузка
3. ТЦ "Мега" (ш. Московское, 15) - выгрузка"""
        
        context.user_data['route'] = {
            'vehicle_info': route_info,
            'checkpoints': [
                {'id': 1, 'name': 'Склад №1', 'address': 'ул. Ленина, 10', 'type': 'загрузка', 'completed': False},
                {'id': 2, 'name': 'Магазин "Продукты"', 'address': 'ул. Мира, 5', 'type': 'выгрузка', 'completed': False},
                {'id': 3, 'name': 'ТЦ "Мега"', 'address': 'ш. Московское, 15', 'type': 'выгрузка', 'completed': False}
            ],
            'current_checkpoint': None
        }
        
        logger.debug(f"Route data for user {user.id}: {context.user_data['route']}")
        
        await update.message.reply_text(
            f"Информация о маршруте:\n{route_info}\n\nВсё верно?",
            reply_markup=get_confirmation_keyboard()
        )
        return 1
    except Exception as e:
        logger.error(f"Start route error for user {user.id}: {e}")
        await update.message.reply_text("Ошибка при создании маршрута. Попробуйте позже.")
        return ConversationHandler.END

async def process_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    choice = update.message.text
    
    if choice == '✅ Всё верно':
        logger.info(f"User {user.id} confirmed route")
        await update.message.reply_text(
            "Путевой лист сформирован! (здесь должно быть фото/документ)",
            reply_markup=get_main_menu()
        )
        await send_checkpoints(update, context)
        return 2
    else:
        logger.info(f"User {user.id} reported route issues")
        await update.message.reply_text(
            "Пожалуйста, сообщите об ошибках диспетчеру.",
            reply_markup=get_main_menu()
        )
        return ConversationHandler.END

async def send_checkpoints(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    checkpoints = context.user_data['route']['checkpoints']
    
    keyboard = []
    for point in checkpoints:
        status = "✅" if point['completed'] else "🔘"
        button = InlineKeyboardButton(
            f"{status} {point['name']} ({point['type']})",
            callback_data=f"checkpoint_{point['id']}"
        )
        keyboard.append([button])
    
    keyboard.append([InlineKeyboardButton("Завершить маршрут", callback_data="finish")])
    
    await update.message.reply_text(
        "Отметьте выполненные точки:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_checkpoint(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    checkpoint_id = int(query.data.split('_')[1])
    
    logger.info(f"User {user.id} toggled checkpoint {checkpoint_id}")
    
    for point in context.user_data['route']['checkpoints']:
        if point['id'] == checkpoint_id:
            point['completed'] = not point['completed']
            break
    
    await send_checkpoints(update, context)
    return 2

async def finish_route(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    logger.info(f"User {user.id} finishing route")
    
    await update.message.reply_text(
        "Введите финальные данные:\n"
        "1. Уровень топлива (л)\n"
        "2. Показания одометра (км)\n\n"
        "Формат: <топливо>, <одометр>\n"
        "Пример: 42, 125700",
        reply_markup=ReplyKeyboardRemove()
    )
    return 3

async def save_final_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.effective_user
    try:
        fuel, odometer = map(str.strip, update.message.text.split(','))
        logger.info(f"User {user.id} submitted final data: fuel={fuel}, odometer={odometer}")
        
        # Здесь должна быть логика сохранения данных
        await update.message.reply_text(
            f"Данные сохранены!\n⛽ Топливо: {fuel} л\n📊 Одометр: {odometer} км\n\n"
            "Маршрут завершен. Для нового маршрута нажмите /start",
            reply_markup=get_main_menu()
        )
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Invalid final data from user {user.id}: {update.message.text}. Error: {e}")
        await update.message.reply_text(
            "Неверный формат данных. Пожалуйста, укажите данные в формате: <топливо>, <одометр>"
        )
        return 3