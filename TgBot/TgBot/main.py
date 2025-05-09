import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
from libs.logger import get_logger
from handlers import base, route
from config.config import TOKEN

logger = get_logger(__name__)

class RouteBot:
    def __init__(self, token: str):
        self.token = token
        logger.info("Initializing bot application")
        try:
            self.application = Application.builder().token(self.token).build()
            self._setup_handlers()
            logger.info("Bot initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}")
            raise

    def _setup_handlers(self):
        logger.debug("Setting up conversation handlers")
        conv_handler = ConversationHandler(
            entry_points=[
                MessageHandler(filters.Regex('^Начать маршрут$'), route.start_route),
                CommandHandler('start', base.start)
            ],
            states={
                0: [],
                1: [MessageHandler(filters.Regex('^(✅ Всё верно|❌ Есть ошибки)$'), route.process_confirmation)],
                2: [
                    CallbackQueryHandler(route.handle_checkpoint, pattern='^checkpoint_'),
                    CallbackQueryHandler(route.finish_route, pattern='^finish$'),
                    MessageHandler(filters.Regex('^Завершить маршрут$'), route.finish_route)
                ],
                3: [MessageHandler(filters.TEXT & ~filters.COMMAND, route.save_final_data)],
                4: [MessageHandler(filters.TEXT & ~filters.COMMAND, route.handle_unfinished_reason)]
            },
            fallbacks=[CommandHandler('cancel', base.cancel)],
        )
        self.application.add_handler(conv_handler)
        logger.debug("Handlers setup completed")

    async def run(self):
        logger.info("Starting bot")
        try:
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            logger.info("Bot started successfully")
            while True: 
                await asyncio.sleep(3600)
        except Exception as e:
            logger.critical(f"Bot crashed: {e}")
            raise
        finally:
            await self.stop()

    async def stop(self):
        logger.info("Stopping bot")
        try:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            logger.info("Bot stopped successfully")
        except Exception as e:
            logger.error(f"Error while stopping bot: {e}")
            raise

async def main():
    bot = RouteBot(TOKEN)
    try: 
        await bot.run()
    except asyncio.CancelledError:
        logger.info("Received shutdown signal")
        await bot.stop()
    except Exception as e:
        logger.critical(f"Unexpected error: {e}")
        await bot.stop()

if __name__ == '__main__':
    asyncio.run(main())