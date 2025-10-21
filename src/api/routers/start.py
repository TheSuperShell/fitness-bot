from logging import Logger
from re import Match
from typing import Any

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.methods import SendMessage
from aiogram.types import (
    KeyboardButton,
    Location,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from message_loader.main import MessageLoader

from ...config import config
from ...db.session import SessionMaker
from ...models.user import User
from ...services.user import create_user, get_telegram_user, get_user_if_exists
from ...utils.time import TimezoneApiError, get_timezone_from_location

router = Router(name=__name__)


class StartStates(StatesGroup):
    EnterHeight = State()
    EnterTimezone = State()


@router.message(CommandStart())
async def start(
    message: Message,
    session_maker: SessionMaker,
    state: FSMContext,
    message_loader: MessageLoader,
) -> SendMessage:
    telegram_user = get_telegram_user(message)
    user: User | None = await get_user_if_exists(telegram_user, session_maker)
    if not user:
        await state.clear()
        await state.update_data(telegram_user=telegram_user)
        await state.set_state(StartStates.EnterHeight)
        return message.answer(message_loader.render_msg("start_height"))
    return message.answer(message_loader.render_msg("hello_user", name=user.full_name))


@router.message(
    StartStates.EnterHeight, F.text.regexp(r"\d{2,3}([\.,]\d{1,2})?").as_("height_m")
)
async def get_height(
    message: Message,
    state: FSMContext,
    height_m: Match[str],
    message_loader: MessageLoader,
) -> SendMessage:
    height: float = float(height_m.string)
    if height < config.height_lower_limit or height > config.height_upper_limit:
        return message.answer(
            message_loader.render_msg(
                "start_height_incorrect",
                min_height=config.height_lower_limit,
                max_height=config.height_upper_limit,
            )
        )
    await state.update_data(height=height)
    await state.set_state(StartStates.EnterTimezone)
    return message.answer(
        message_loader.render_msg("start_timezone"),
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Share my Location", request_location=True)]]
        ),
    )


@router.message(StartStates.EnterHeight)
def incorrect_height(message: Message, message_loader: MessageLoader) -> SendMessage:
    return message.answer(message_loader.render_msg("start_height_incorrect_format"))


@router.message(StartStates.EnterTimezone, F.text.regexp(r"^[\+-]\d{1,2}$").as_("gmt"))
async def timezone_from_gmt(
    message: Message,
    state: FSMContext,
    session_maker: SessionMaker,
    logger: Logger,
    gmt: Match[str],
    message_loader: MessageLoader,
) -> SendMessage:
    if abs(int(gmt.string)) > 12:
        return message.answer(message_loader.render_msg("start_gmt_incorrect"))
    timezone: str = "Etc/GMT" + gmt.string
    data: dict[str, Any] = await state.get_data()
    await state.clear()
    user = await create_user(
        data["telegram_user"], session_maker, logger, data["height"], timezone
    )
    logger.info(f"created new user for telegram id {user.telegram_id}")
    return message.answer(
        message_loader.render_msg("start_welcome", name=user.full_name),
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(StartStates.EnterTimezone, F.location.as_("location"))
async def timezone_from_location(
    message: Message,
    state: FSMContext,
    session_maker: SessionMaker,
    logger: Logger,
    location: Location,
    message_loader: MessageLoader,
) -> SendMessage:
    timezone: str
    try:
        timezone = get_timezone_from_location(location)
    except TimezoneApiError as e:
        logger.error(f"timezone api error: {e}")
        return message.answer(
            message_loader.render_msg("start_timezone_erroe"),
            reply_markup=ReplyKeyboardRemove(),
        )
    data: dict[str, Any] = await state.get_data()
    await state.clear()
    logger.debug(f"{location.latitude = }; {location.longitude = }")
    user = await create_user(
        data["telegram_user"], session_maker, logger, data["height"], timezone
    )
    logger.info(f"created new user for telegram id {user.telegram_id}")
    return message.answer(
        message_loader.render_msg("start_welcome", name=user.full_name),
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(StartStates.EnterTimezone)
def no_location(message: Message, message_loader: MessageLoader) -> SendMessage:
    return message.answer(
        message_loader.render_msg("start_timezone_incorrect_format"),
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Share my Location", request_location=True)]]
        ),
    )
