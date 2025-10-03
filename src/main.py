import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_API_KEY
from logger import setup_logging, get_logger
from api.routers import start_router


async def startup_event(dispatcher: Dispatcher) -> None:
    dispatcher["log_listener"] = setup_logging()
    dispatcher["logger"] = get_logger()


async def shutdown_event(dispatcher: Dispatcher) -> None:
    dispatcher["log_listener"].stop()


async def main() -> None:
    dp = Dispatcher()
    dp.startup.register(startup_event)
    dp.shutdown.register(shutdown_event)
    dp.include_routers(start_router)
    bot = Bot(
        token=BOT_API_KEY,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2),
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
