import asyncio
from loguru import logger

from src.handlers import user_handler, cryptopay_handler
from src.methods.database.init_db import init_databases
from src.misc import bot, dp, cp
# from src.methods.payment import payment_checker


def register_handlers():
    dp.include_routers(user_handler.router)
    # dp.include_routers(cryptopay_handler.router)  # Регистрация CryptoPay обработчиков

# Платежный поток (можно временно отключить)
async def payment_polling():
    # await payment_checker.run_order_status_checker()  # Оставь, если нужно
    pass

# Инициализация баз данных
async def on_startup():
    await init_databases()  # Инициализация всех баз данных
    logger.info("Базы данных успешно инициализированы")

async def main():
    await on_startup()  # Вызов инициализации баз данных
    register_handlers() # Регистрация обработчиков
    # aaio_polling_task = asyncio.create_task(payment_polling())  # Отключено, если не нужно
    app = await cp.get_me()
    print(app.name)
    # Запускаем все задачи параллельно
    await asyncio.gather(
        dp.start_polling(bot),  # Telegram-бот
        
        cp.start_polling(),       # CryptoPay
        # aaio_polling_task      # Закомментировано для исключения третьего потока
    )

if __name__ == "__main__":
    logger.add('src/logs/logs.log', format="{time} {level} {message}", level='DEBUG')   

    asyncio.run(main())