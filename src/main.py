import asyncio
import logging
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message
from aiogram.methods.send_message import SendMessage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_API_KEY
from logger import setup_logging, get_logger


router = Router(name=__name__)


@router.message()
async def hello(message: Message, logger: logging.Logger) -> SendMessage:
    current_user = message.from_user
    if current_user is None:
        logger.error("there is not current user")
        return message.answer("Oops, something went wrong")
    logger.info("Just a test log")
    return message.answer(f"Hello, {current_user.full_name}")


async def startup_event(dispatcher: Dispatcher) -> None:
    dispatcher["log_listener"] = setup_logging()
    dispatcher["logger"] = get_logger()


async def shutdown_event(dispatcher: Dispatcher) -> None:
    dispatcher["log_listener"].stop()


async def main() -> None:
    dp = Dispatcher()
    dp.startup.register(startup_event)
    dp.shutdown.register(shutdown_event)
    dp.include_routers(router)
    bot = Bot(
        token=BOT_API_KEY,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2),
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
