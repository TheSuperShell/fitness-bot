from logging import Logger
from re import Match
from typing import Any

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.methods import SendMessage
from aiogram.types import Message
from pydantic import ValidationError

from config import config
from db.session import SessionMaker
from models.stats import ParamRecord
from models.user import User, UserNotRegisteredError
from services.stats import save_record
from services.user import get_telegram_user, get_user_if_exists

router = Router(name=__name__)


class RecordForm(StatesGroup):
    enter_weight = State()
    enter_fat_p = State()
    enter_muscle_p = State()


@router.message(Command("add_record"))
async def add_record(
    message: Message, state: FSMContext, session_maker: SessionMaker, logger: Logger
) -> SendMessage:
    telegram_user = get_telegram_user(message)
    user: User | None = await get_user_if_exists(telegram_user, session_maker)
    if not user or not user.id:
        raise UserNotRegisteredError(telegram_user.id)
    await state.clear()
    await state.update_data(user_id=user.id, height=user.height)
    await state.set_state(RecordForm.enter_weight)
    return message.answer("Enter your current weight in kg")


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
    return message.answer("Enter fat %\. Enter `skip` if you don't want to record it")  # pyright: ignore[reportInvalidStringEscapeSequence]


@router.message(RecordForm.enter_weight)
async def enter_weight_incorrect_format(message: Message) -> SendMessage:
    return message.answer(
        "Please enter weight in the correct format, for example:"
        " **100** or **100\.05** or **100,05**"  # pyright: ignore[reportInvalidStringEscapeSequence]
    )


@router.message(RecordForm.enter_fat_p, F.text.casefold() == "skip")
async def skip_fat_p(message: Message, state: FSMContext) -> SendMessage:
    await state.set_state(RecordForm.enter_muscle_p)
    return message.answer(
        "Enter you muscle %\. Enter `skip` if you don't want to record it"  # pyright: ignore[reportInvalidStringEscapeSequence]
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
        "Enter you muscle %\. Enter `skip` if you don't want to record it"  # pyright: ignore[reportInvalidStringEscapeSequence]
    )


@router.message(RecordForm.enter_fat_p)
async def record_fat_p_incorrect_format(message: Message) -> SendMessage:
    return message.answer(
        "Please enter fat \% in the correct format, for example 25 or 0\.25 or 0,75"  # pyright: ignore[reportInvalidStringEscapeSequence]
    )


@router.message(RecordForm.enter_muscle_p, F.text.casefold() == "skip")
async def skip_muscle_p(
    message: Message, state: FSMContext, logger: Logger, session_maker: SessionMaker
) -> SendMessage:
    data = await state.get_data()
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
