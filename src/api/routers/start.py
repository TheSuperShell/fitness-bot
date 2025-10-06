from logging import Logger

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.methods import SendMessage
from aiogram.types import Message

from db.session import SessionMaker
from services.user import get_or_create_user, get_telegram_user

router = Router(name=__name__)


@router.message(CommandStart())
async def start(
    message: Message, session_maker: SessionMaker, logger: Logger
) -> SendMessage:
    telegram_user = get_telegram_user(message)
    user = await get_or_create_user(telegram_user, session_maker, logger)
    logger.info(
        f"loaded user {user.telegram_id}; amount of records: {len(user.records)}"
    )
    return message.answer(f"Hello, {user.full_name}")
