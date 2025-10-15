from logging import Logger
from re import Match
from typing import Any

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.methods import SendMessage
from aiogram.types import CallbackQuery, Message
from aiogram_timepicker.main import TimePickerBuilder, TimeQuery
from pydantic import ValidationError

from config import config
from db.session import SessionMaker
from models.stats import ParamRecord
from models.user import User, UserNotRegisteredError
from services.stats import save_record
from services.user import get_telegram_user, get_user_if_exists
from utils.time import current_timestamp_utc

router = Router(name=__name__)

time_picker_builder = TimePickerBuilder(name="stats")


class RecordForm(StatesGroup):
    enter_weight = State()
    enter_fat_p = State()
    enter_muscle_p = State()
    enter_time = State()


@router.message(Command("add_record"))
async def add_record(
    message: Message, state: FSMContext, session_maker: SessionMaker, logger: Logger
) -> SendMessage:
    telegram_user = get_telegram_user(message)
    user: User | None = await get_user_if_exists(telegram_user, session_maker)
    if not user or not user.id:
        raise UserNotRegisteredError(telegram_user.id)
    await state.clear()
    await state.update_data(user_id=user.id, height=user.height, timezone=user.timezone)
    await state.set_state(RecordForm.enter_time)
    time_picker = time_picker_builder.build_from_timestamp_tz(
        user.timestamp_in_users_timezone(current_timestamp_utc())
    )
    return message.answer(
        "Please choose the record time",
        reply_markup=time_picker.get_keyboard(),
    )


@router.callback_query(RecordForm.enter_time, time_picker_builder.ok_filter())
async def ok_time(
    query: CallbackQuery, callback_data: TimeQuery, state: FSMContext, logger: Logger
) -> SendMessage:
    if not query.message:
        raise ValueError("no message")
    timezone = (await state.get_data())["timezone"]
    logger.debug(f"{callback_data.get_datetime_today_utc(timezone)}")
    await state.update_data(measured_at=callback_data.get_datetime_today_utc(timezone))
    await state.set_state(RecordForm.enter_weight)
    return query.message.answer("Please enter your weight messurement in kg")


@router.callback_query(RecordForm.enter_time, time_picker_builder.filter())
async def switch_time(
    query: CallbackQuery, callback_data: TimeQuery, bot: Bot, state: FSMContext
) -> None:
    time_picker = time_picker_builder.build_from_callback(callback_data)
    if not query.message:
        return
    await bot.edit_message_reply_markup(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        reply_markup=time_picker.get_keyboard(),
    )


@router.message(
    RecordForm.enter_weight, F.text.regexp(r"^\s*\d+([\.,]\d+)?\s*$").as_("weight_m")
)
async def enter_weight(
    message: Message, state: FSMContext, weight_m: Match[str]
) -> SendMessage:
    weight: float = float(weight_m.string.strip())
    if weight > config.weight_upper_limit or weight < config.weight_lower_limit:
        return message.answer(
            f"Weight should be between **{config.weight_lower_limit:.0f}** kg and "
            f"**{config.weight_upper_limit:.0f}** kg"
        )
    await state.update_data(weight=weight)
    await state.set_state(RecordForm.enter_fat_p)
    return message.answer("Enter fat %\. Enter /skip if you don't want to record it")  # pyright: ignore[reportInvalidStringEscapeSequence]


@router.message(RecordForm.enter_weight)
async def enter_weight_incorrect_format(message: Message) -> SendMessage:
    return message.answer(
        "Please enter weight in the correct format, for example:"
        " **100** or **100\.05** or **100,05**"  # pyright: ignore[reportInvalidStringEscapeSequence]
    )


@router.message(RecordForm.enter_fat_p, F.text.casefold() == "skip")
@router.message(RecordForm.enter_fat_p, Command("skip"))
async def skip_fat_p(message: Message, state: FSMContext) -> SendMessage:
    await state.set_state(RecordForm.enter_muscle_p)
    await state.update_data(fat_percent=None)
    return message.answer(
        "Enter you muscle %\. Enter /skip if you don't want to record it"  # pyright: ignore[reportInvalidStringEscapeSequence]
    )


@router.message(
    RecordForm.enter_fat_p, F.text.regexp(r"^\d{1,2}$|^0[\.,]\d{1,2}").as_("fat_p_m")
)
async def record_fat_p(
    message: Message, state: FSMContext, fat_p_m: Match[str]
) -> SendMessage:
    fat_p: float = float(fat_p_m.string)
    fat_p /= 100 if fat_p >= 1 else 1
    await state.update_data(fat_percent=fat_p)
    await state.set_state(RecordForm.enter_muscle_p)
    return message.answer(
        "Enter you muscle %\. Enter /skip if you don't want to record it"  # pyright: ignore[reportInvalidStringEscapeSequence]
    )


@router.message(RecordForm.enter_fat_p)
async def record_fat_p_incorrect_format(message: Message) -> SendMessage:
    return message.answer(
        "Please enter fat \% in the correct format, for example 25 or 0\.25 or 0,75"  # pyright: ignore[reportInvalidStringEscapeSequence]
    )


@router.message(RecordForm.enter_muscle_p, F.text.casefold() == "skip")
@router.message(RecordForm.enter_muscle_p, Command("skip"))
async def skip_muscle_p(
    message: Message, state: FSMContext, logger: Logger, session_maker: SessionMaker
) -> SendMessage:
    data = await state.update_data(muscle_percent=None)
    await state.clear()
    result = data_to_record(data, message, logger)
    if isinstance(result, SendMessage):
        return result
    record = await save_record(session_maker, result)
    return message.answer(f"Record **{record}** has been saved")


@router.message(
    RecordForm.enter_muscle_p,
    F.text.regexp(r"^\d{1,2}$|^0[\.,]\d{1,2}").as_("muscle_p_m"),
)
async def record_muscle_p(
    message: Message,
    state: FSMContext,
    muscle_p_m: Match[str],
    logger: Logger,
    session_maker: SessionMaker,
) -> SendMessage:
    muscle_p: float = float(muscle_p_m.string)
    muscle_p /= 100 if muscle_p >= 1 else 1
    data: dict[str, Any] = await state.update_data(muscle_percent=muscle_p)
    await state.clear()
    result = data_to_record(data, message, logger)
    if isinstance(result, SendMessage):
        return result
    record = await save_record(session_maker, result)
    return message.answer(f"Record **{record}** has been saved")


def data_to_record(
    data: dict[str, Any], message: Message, logger: Logger
) -> ParamRecord | SendMessage:
    try:
        return ParamRecord.model_validate(data)
    except ValidationError as e:
        validation_errors = "; ".join(
            [str(err).replace("{", "\\{").replace("}", "\\}") for err in e.errors()]
        )
        logger.warning(
            f"detected validation errors for {data['user_id']} user:"
            f" {validation_errors}"
        )
        return message.answer("Validation errors during creation of the record")


@router.message(RecordForm.enter_muscle_p)
async def record_muscle_p_incorrect_format(message: Message) -> SendMessage:
    return message.answer(
        "Please enter muscle \% in the correct format, for example 75 or 0\.75 or 0,75"  # pyright: ignore[reportInvalidStringEscapeSequence]
    )
