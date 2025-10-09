from logging import Logger
from re import Match
from typing import Any

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.methods import SendMessage
from aiogram.types import Message

from config import config
from db.session import SessionMaker
from models.user import User
from services.user import create_user, get_telegram_user, get_user_if_exists

router = Router(name=__name__)


class StartStates(StatesGroup):
    EnterHeight = State()


@router.message(CommandStart())
async def start(
    message: Message, session_maker: SessionMaker, state: FSMContext
) -> SendMessage:
    telegram_user = get_telegram_user(message)
    user: User | None = await get_user_if_exists(telegram_user, session_maker)
    if not user:
        await state.clear()
        await state.update_data(telegram_user=telegram_user)
        await state.set_state(StartStates.EnterHeight)
        return message.answer("Please enter your current height in cm:")
    return message.answer(f"Hello, {user.full_name}")


@router.message(
    StartStates.EnterHeight, F.text.regexp(r"\d{2,3}([\.,]\d{1,2})?").as_("height_m")
)
async def get_height(
    message: Message,
    session_maker: SessionMaker,
    logger: Logger,
    state: FSMContext,
    height_m: Match[str],
) -> SendMessage:
    height: float = float(height_m.string)
    if height < config.height_lower_limit or height > config.height_upper_limit:
        return message.answer(
            f"Height must be between {config.height_lower_limit:.0f} "
            f"and {config.height_upper_limit:.0f} cm"
        )
    data: dict[str, Any] = await state.get_data()
    user = await create_user(data["telegram_user"], session_maker, logger, height)
    logger.info(f"created new user for telegram id {user.telegram_id}")
    return message.answer(f"Welcome {user.full_name}")
