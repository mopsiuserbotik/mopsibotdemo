import asyncio
from accounts_manager import AccountsManager
from utils.logger import setup_logger

logger = setup_logger()

async def main():
    manager = AccountsManager()
    session_name = await manager.run_menu()
    if not session_name:
        logger.warning("Сессия не выбрана. Завершение работы.")
        return

    logger.info(f"Выбран аккаунт: \033[94m{session_name}\033[0m")

    from core.client import UserBot
    from handlers import register_all_handlers

    bot = UserBot(session_name)
    register_all_handlers(bot.client, logger)
    logger.blueinfo("Команды успешно зарегистрированы")

    await bot.start()
    logger.blueinfo("Клиент запущен, юзербот работает")

    try:
        await bot.client.run_until_disconnected()
    except asyncio.CancelledError:
        logger.info("Юзербот остановлен пользователем")
    except Exception as e:
        logger.exception(f"Необработанная ошибка: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[INFO] Завершение работы по Ctrl+C") 