from logging import Logger

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.methods import SendMessage
from aiogram.types import Message

from db.session import SessionMaker
from models.user import User
from services.user import create_user, get_telegram_user, get_user_if_exists

router = Router(name=__name__)


@router.message(CommandStart())
async def start(
    message: Message, session_maker: SessionMaker, logger: Logger
) -> SendMessage:
    telegram_user = get_telegram_user(message)
    user: User | None = await get_user_if_exists(telegram_user, session_maker)
    if not user:
        user = await create_user(telegram_user, session_maker, logger, 170.0)
        return message.answer(f"Hello, {user.full_name}")
    return message.answer(f"Hello, {user.full_name}")
