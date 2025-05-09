import asyncio
from typing import Any
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes


class TgBot:
    def __init__(self, token: str):
        self.token = token
        self.application = Application.builder().token(self.token).build()
        
        # Регистрируем обработчики
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.echo_message))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /start"""
        await update.message.reply_text("Привет! Я эхо-бот. Отправь мне любое сообщение, и я отвечу тем же.")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /help"""
        await update.message.reply_text("Просто отправь мне сообщение, и я его повторю!")
    
    async def echo_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик текстовых сообщений"""
        user_message = update.message.text
        await update.message.reply_text(f"Вы сказали: {user_message}")
    
    async def run(self) -> None:
        """Запуск бота"""
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        # Бесконечный цикл для поддержания работы бота
        while True:
            await asyncio.sleep(3600)
    
    async def stop(self) -> None:
        """Остановка бота"""
        await self.application.updater.stop()
        await self.application.stop()
        await self.application.shutdown()


async def main():
    # Замените 'YOUR_BOT_TOKEN' на реальный токен вашего бота
    bot = TgBot(token='YOUR_BOT_TOKEN')
    
    try:
        await bot.run()
    except asyncio.CancelledError:
        await bot.stop()


if __name__ == '__main__':
    asyncio.run(main())