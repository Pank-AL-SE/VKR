from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu():
    """Только основное меню"""
    return ReplyKeyboardMarkup([['Начать маршрут']], resize_keyboard=True)

def get_confirmation_keyboard():
    """Только для подтверждения маршрута"""
    return ReplyKeyboardMarkup([['✅ Всё верно', '❌ Есть ошибки']], resize_keyboard=True)

def get_checkpoints_keyboard(checkpoints):
    """Только для отметки пунктов"""
    keyboard = []
    for point in checkpoints:
        status = "✅" if point['completed'] else "🔘"
        button = InlineKeyboardButton(
            f"{status} {point['name']} ({point['type']})",
            callback_data=f"checkpoint_{point['id']}"
        )
        keyboard.append([button])
    
    keyboard.append([InlineKeyboardButton("Завершить маршрут", callback_data="finish")])
    
    return InlineKeyboardMarkup(keyboard)

def get_reason_keyboard():
    """Клавиатура для ввода причины"""
    return ReplyKeyboardMarkup([
        ['Пропустить и завершить'],
        ['Отменить завершение']
    ], resize_keyboard=True)