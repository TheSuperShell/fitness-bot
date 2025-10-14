from logging import Logger
from re import Match
from typing import Any

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.methods import SendMessage
from aiogram.types import KeyboardButton, Location, Message, ReplyKeyboardMarkup

from config import config
from db.session import SessionMaker
from models.user import User
from services.user import create_user, get_telegram_user, get_user_if_exists
from utils.time import TimezoneApiError, get_timezone_from_location

router = Router(name=__name__)


class StartStates(StatesGroup):
    EnterHeight = State()
    EnterTimezone = State()


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
    state: FSMContext,
    height_m: Match[str],
) -> SendMessage:
    height: float = float(height_m.string)
    if height < config.height_lower_limit or height > config.height_upper_limit:
        return message.answer(
            f"Height must be between {config.height_lower_limit:.0f} "
            f"and {config.height_upper_limit:.0f} cm"
        )
    await state.update_data(height=height)
    await state.set_state(StartStates.EnterTimezone)
    return message.answer(
        "Now we need to learn your timezone\. "  # pyright: ignore[reportInvalidStringEscapeSequence]
        "Please share your location "
        "\(we will only save your timezone based on the location\)",  # pyright: ignore[reportInvalidStringEscapeSequence]
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Share my Location", request_location=True)]]
        ),
    )


@router.message(StartStates.EnterHeight)
def incorrect_height(message: Message) -> SendMessage:
    return message.answer(
        "Please enter your weight in the correct format, for example 175"
    )


@router.message(StartStates.EnterTimezone, F.location.as_("location"))
async def timezone_from_location(
    message: Message,
    state: FSMContext,
    session_maker: SessionMaker,
    logger: Logger,
    location: Location,
) -> SendMessage:
    data: dict[str, Any] = await state.get_data()
    await state.clear()
    logger.debug(f"{location.latitude = }; {location.longitude = }")
    timezone: str
    try:
        timezone = get_timezone_from_location(location)
    except TimezoneApiError as e:
        logger.error(f"timezone api error: {e}")
        timezone = "UTC"
    user = await create_user(
        data["telegram_user"], session_maker, logger, data["height"], timezone
    )
    logger.info(f"created new user for telegram id {user.telegram_id}")
    return message.answer(
        f"Your timezone is set to be {user.timezone}\nWelcome {user.full_name}"
    )


@router.message(StartStates.EnterTimezone)
def no_location(message: Message) -> SendMessage:
    return message.answer(
        "Please send a location",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Share my Location", request_location=True)]]
        ),
    )
