import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message
from aiogram.methods.send_message import SendMessage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import BOT_API_KEY


router = Router(name=__name__)


@router.message()
async def hello(message: Message) -> SendMessage:
    current_user = message.from_user
    if current_user is None:
        return message.answer("Oops, something went wrong")
    return message.answer(f"Hello, {current_user.full_name}")


async def main() -> None:
    dp = Dispatcher()
    dp.include_routers(router)
    bot = Bot(
        token=BOT_API_KEY,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2),
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
