from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu():
    return ReplyKeyboardMarkup([['Начать маршрут']], resize_keyboard=True)

def get_confirmation_keyboard():
    return ReplyKeyboardMarkup([['✅ Всё верно', '❌ Есть ошибки']], resize_keyboard=True)

def get_checkpoints_keyboard(checkpoints):
    keyboard = []
    for point in checkpoints:
        status = "✅" if point['completed'] else "🔘"
        button = InlineKeyboardButton(
            f"{status} {point['name']} ({point['type']})",
            callback_data=f"checkpoint_{point['id']}"
        )
        keyboard.append([button])
    
    keyboard.append([
        InlineKeyboardButton("Изменить порядок", callback_data="change_order"),
        InlineKeyboardButton("Завершить маршрут", callback_data="finish_route")
    ])
    
    return InlineKeyboardMarkup(keyboard)