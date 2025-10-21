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
from message_loader.main import MessageLoader

from ...config import config
from ...db.session import SessionMaker
from ...models.stats import ParamRecord
from ...models.user import User
from ...services.stats import save_record
from ...services.user import get_user
from ...utils.time import current_timestamp_utc

router = Router(name=__name__)

time_picker_builder = TimePickerBuilder(name="stats")


class RecordForm(StatesGroup):
    enter_weight = State()
    enter_fat_p = State()
    enter_muscle_p = State()
    enter_time = State()


@router.message(Command("add_record"))
async def add_record(
    message: Message,
    state: FSMContext,
    session_maker: SessionMaker,
    message_loader: MessageLoader,
) -> SendMessage:
    user: User = await get_user(message, session_maker)
    await state.clear()
    await state.update_data(user_id=user.id, height=user.height, timezone=user.timezone)
    await state.set_state(RecordForm.enter_time)
    time_picker = time_picker_builder.build_from_timestamp_tz(
        user.timestamp_in_users_timezone(current_timestamp_utc())
    )
    return message.answer(
        message_loader.render_msg("stats_time"), reply_markup=time_picker.get_keyboard()
    )


@router.callback_query(RecordForm.enter_time, time_picker_builder.ok_filter())
async def ok_time(
    query: CallbackQuery,
    callback_data: TimeQuery,
    state: FSMContext,
    logger: Logger,
    message_loader: MessageLoader,
) -> SendMessage:
    if not query.message:
        raise ValueError("no message")
    timezone = (await state.get_data())["timezone"]
    logger.debug(f"{callback_data.get_datetime_today_utc(timezone)}")
    await state.update_data(measured_at=callback_data.get_datetime_today_utc(timezone))
    await state.set_state(RecordForm.enter_weight)
    return query.message.answer(message_loader.render_msg("stats_weight"))


@router.callback_query(RecordForm.enter_time, time_picker_builder.filter())
async def switch_time(query: CallbackQuery, callback_data: TimeQuery, bot: Bot) -> None:
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
    message: Message,
    state: FSMContext,
    weight_m: Match[str],
    message_loader: MessageLoader,
) -> SendMessage:
    weight: float = float(weight_m.string.strip())
    if weight > config.weight_upper_limit or weight < config.weight_lower_limit:
        return message.answer(
            message_loader.render_msg(
                "stats_weight_incorrect",
                max_weight=config.weight_upper_limit,
                min_weight=config.weight_lower_limit,
            )
        )
    await state.update_data(weight=weight)
    await state.set_state(RecordForm.enter_fat_p)
    return message.answer(message_loader.render_msg("stats_fat"))


@router.message(RecordForm.enter_weight)
async def enter_weight_incorrect_format(
    message: Message, message_loader: MessageLoader
) -> SendMessage:
    return message.answer(message_loader.render_msg("stats_weight_incorrect_format"))


@router.message(RecordForm.enter_fat_p, F.text.casefold() == "skip")
@router.message(RecordForm.enter_fat_p, Command("skip"))
async def skip_fat_p(
    message: Message, state: FSMContext, message_loader: MessageLoader
) -> SendMessage:
    await state.set_state(RecordForm.enter_muscle_p)
    await state.update_data(fat_percent=None)
    return message.answer(message_loader.render_msg("stats_muscle"))


@router.message(
    RecordForm.enter_fat_p, F.text.regexp(r"^\d{1,2}$|^0[\.,]\d{1,2}").as_("fat_p_m")
)
async def record_fat_p(
    message: Message,
    state: FSMContext,
    fat_p_m: Match[str],
    message_loader: MessageLoader,
) -> SendMessage:
    fat_p: float = float(fat_p_m.string)
    fat_p /= 100 if fat_p >= 1 else 1
    await state.update_data(fat_percent=fat_p)
    await state.set_state(RecordForm.enter_muscle_p)
    return message.answer(message_loader.render_msg("stats_muscle"))


@router.message(RecordForm.enter_fat_p)
async def record_fat_p_incorrect_format(
    message: Message, message_loader: MessageLoader
) -> SendMessage:
    return message.answer(message_loader.render_msg("stats_fat_incorrect_format"))


@router.message(RecordForm.enter_muscle_p, F.text.casefold() == "skip")
@router.message(RecordForm.enter_muscle_p, Command("skip"))
async def skip_muscle_p(
    message: Message,
    state: FSMContext,
    session_maker: SessionMaker,
    message_loader: MessageLoader,
) -> SendMessage:
    data = await state.update_data(muscle_percent=None)
    await state.clear()
    result = ParamRecord.model_validate(data)
    record = await save_record(session_maker, result)
    return message.answer(
        message_loader.render_msg("stats_record_save", record_data=str(record))
    )


@router.message(
    RecordForm.enter_muscle_p,
    F.text.regexp(r"^\d{1,2}$|^0[\.,]\d{1,2}").as_("muscle_p_m"),
)
async def record_muscle_p(
    message: Message,
    state: FSMContext,
    muscle_p_m: Match[str],
    session_maker: SessionMaker,
    message_loader: MessageLoader,
) -> SendMessage:
    muscle_p: float = float(muscle_p_m.string)
    muscle_p /= 100 if muscle_p >= 1 else 1
    data: dict[str, Any] = await state.update_data(muscle_percent=muscle_p)
    await state.clear()
    result = ParamRecord.model_validate(data)
    record = await save_record(session_maker, result)
    return message.answer(
        message_loader.render_msg("stats_record_save", record_data=str(record))
    )


@router.message(RecordForm.enter_muscle_p)
async def record_muscle_p_incorrect_format(
    message: Message, message_loader: MessageLoader
) -> SendMessage:
    return message.answer(message_loader.render_msg("stats_muscle_incorrect_format"))
