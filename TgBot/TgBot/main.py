import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
import sys
sys.path.append('..')
from handlers import base, route
from libs.keyboards import *
from config.config import TOKEN

class RouteBot:
    def __init__(self, token: str):
        self.token = token
        self.application = Application.builder().token(self.token).build()
        self._setup_handlers()

    def _setup_handlers(self):
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', base.start)],
            states={
                0: [MessageHandler(filters.Regex('^Начать маршрут$'), route.start_route)],
                # 1: [...],  # Добавьте остальные состояния
            },
            fallbacks=[CommandHandler('cancel', base.cancel)],
        )
        self.application.add_handler(conv_handler)

    async def run(self):
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        while True: await asyncio.sleep(3600)

    async def stop(self):
        await self.application.updater.stop()
        await self.application.stop()
        await self.application.shutdown()

async def main():
    bot = RouteBot(TOKEN)
    try: await bot.run()
    except asyncio.CancelledError: await bot.stop()

if __name__ == '__main__':
    asyncio.run(main())