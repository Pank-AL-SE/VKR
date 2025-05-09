from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, CallbackQueryHandler, ConversationHandler
from libs.keyboards import get_confirmation_keyboard, get_main_menu, get_reason_keyboard, get_checkpoints_keyboard
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
        
        await update.message.reply_text(
            f"Информация о маршруте:\n{route_info}\n\nВсё верно?",
            reply_markup=get_confirmation_keyboard()
        )
        return 1  # Переходим к состоянию подтверждения
    except Exception as e:
        logger.error(f"Start route error for user {user.id}: {e}")
        await update.message.reply_text(
            "Ошибка при создании маршрута. Попробуйте позже.",
            reply_markup=get_main_menu()
        )
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
    """Универсальная функция отправки/обновления списка точек"""
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
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.callback_query:
        # Редактируем существующее сообщение для CallbackQuery
        await update.callback_query.edit_message_text(
            text="Отметьте выполненные точки:",
            reply_markup=reply_markup
        )
    else:
        # Отправляем новое сообщение для обычного Message
        await update.message.reply_text(
            text="Отметьте выполненные точки:",
            reply_markup=reply_markup
        )

async def handle_checkpoint(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка нажатия на точку маршрута"""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    checkpoint_id = int(query.data.split('_')[1])
    
    logger.info(f"User {user.id} toggled checkpoint {checkpoint_id}")
    
    # Обновляем статус точки
    for point in context.user_data['route']['checkpoints']:
        if point['id'] == checkpoint_id:
            point['completed'] = not point['completed']
            break
    
    # Обновляем сообщение с кнопками
    await send_checkpoints(update, context)
    return 2

async def finish_route(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка завершения маршрута с проверкой незавершенных пунктов"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        chat_id = query.message.chat_id
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=query.message.message_id,
            text="Проверяем выполнение маршрута..."
        )
    else:
        chat_id = update.message.chat_id

    # Получаем текущее состояние чекпоинтов (актуальные данные)
    current_unfinished = [p for p in context.user_data['route']['checkpoints'] if not p['completed']]
    
    if current_unfinished:
        # Обновляем список незавершенных пунктов в user_data
        context.user_data['unfinished_points'] = current_unfinished
        points_list = "\n".join(f"{p['id']}. {p['name']}" for p in current_unfinished)
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"⚠️ У вас есть незавершенные пункты:\n{points_list}\n"
                 "Пожалуйста, укажите причину или выберите действие:",
            reply_markup=get_reason_keyboard()
        )
        return 4
    else:
        # Если нет незавершенных пунктов, сразу запрашиваем финальные данные
        await request_final_data(context, chat_id)
        return 3

async def handle_unfinished_reason(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработка причины незавершенных пунктов с кнопками"""
    user = update.effective_user
    chat_id = update.message.chat_id
    user_choice = update.message.text

    # Всегда проверяем актуальное состояние чекпоинтов
    current_unfinished = [p for p in context.user_data['route']['checkpoints'] if not p['completed']]
    
    if not current_unfinished:
        # Если пользователь тем временем отметил все пункты
        await update.message.reply_text(
            "Все пункты теперь завершены. Переходим к завершению маршрута...",
            reply_markup=ReplyKeyboardRemove()
        )
        await request_final_data(context, chat_id)
        return 3

    if user_choice == 'Пропустить и завершить':
        logger.info(f"User {user.id} skipped reason for unfinished points")
        # Сохраняем только действительно незавершенные пункты
        context.user_data['unfinished_points'] = current_unfinished
        await update.message.reply_text(
            "Переходим к завершению маршрута...",
            reply_markup=ReplyKeyboardRemove()
        )
        await request_final_data(context, chat_id)
        return 3
        
    elif user_choice == 'Отменить завершение':
        logger.info(f"User {user.id} canceled route finishing")
        await update.message.reply_text(
            "Завершение маршрута отменено. Продолжаем работу.",
            reply_markup=get_checkpoints_keyboard(context.user_data['route']['checkpoints'])
        )
        return 2
        
    else:
        # Пользователь ввел текст причины
        reason = user_choice
        # Обновляем только текущие незавершенные пункты
        for point in current_unfinished:
            point['reason'] = reason
        
        logger.info(f"User {user.id} provided reason: {reason}")
        context.user_data['unfinished_points'] = current_unfinished
        await update.message.reply_text(
            f"Причина сохранена: {reason}",
            reply_markup=ReplyKeyboardRemove()
        )
        await request_final_data(context, chat_id)
        return 3

async def save_final_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Сохранение финальных данных"""
    user = update.effective_user
    try:
        fuel, odometer = map(str.strip, update.message.text.split(','))
        
        # Формируем отчет
        report = f"Данные сохранены!\n⛽ Топливо: {fuel} л\n📊 Одометр: {odometer} км"
        
        # Проверяем актуальные незавершенные пункты
        current_unfinished = [p for p in context.user_data['route']['checkpoints'] if not p['completed']]
        
        if current_unfinished:
            # Используем причины из user_data или устанавливаем "не указана"
            unfinished_with_reasons = []
            for p in current_unfinished:
                reason = p.get('reason', 'не указана')
                unfinished_with_reasons.append(f"❌ {p['name']} (причина: {reason})")
            
            report += f"\n\nНезавершенные пункты:\n" + "\n".join(unfinished_with_reasons)
        
        await update.message.reply_text(
            report + "\n\nМаршрут завершен. Для нового маршрута нажмите /start",
            reply_markup=get_main_menu()
        )
        
        logger.info(f"User {user.id} finished route. Fuel: {fuel}, Odometer: {odometer}. "
                   f"Unfinished: {len(current_unfinished)}")
        
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Invalid final data from user {user.id}: {update.message.text}. Error: {e}")
        await update.message.reply_text(
            "Неверный формат данных. Пожалуйста, укажите данные в формате: <топливо>, <одометр>"
        )
        return 3
    
async def request_final_data(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    """Общая функция запроса финальных данных"""
    await context.bot.send_message(
        chat_id=chat_id,
        text="Введите финальные данные:\n"
             "1. Уровень топлива (л)\n"
             "2. Показания одометра (км)\n\n"
             "Формат: <топливо>, <одометр>\n"
             "Пример: 42, 125700",
        reply_markup=get_main_menu()
    )