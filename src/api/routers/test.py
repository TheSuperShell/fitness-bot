import datetime

from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.methods import SendMessage
from aiogram.types import CallbackQuery, Message
from aiogram_timepicker import TimePickerBuilder, TimeQuery

router = Router(name=__name__)

time_picker_builder = TimePickerBuilder(name="test")


@router.message(Command("test_time"))
def test_time(message: Message) -> SendMessage:
    time_picker = time_picker_builder.build_from_timestamp(
        datetime.datetime.now(datetime.UTC)
    )
    return message.answer("Hello", reply_markup=time_picker.get_keyboard())


@router.callback_query(time_picker_builder.ok_filter())
def test_time_ok(query: CallbackQuery, callback_data: TimeQuery) -> SendMessage:
    if not query.message:
        raise ValueError("no message")
    return query.message.answer(
        f"Hour: {callback_data.hour}, Minute: {callback_data.minute}"
    )


@router.callback_query(time_picker_builder.filter())
async def test_time_callback(
    query: CallbackQuery, callback_data: TimeQuery, bot: Bot
) -> None:
    if query.message is None:
        raise ValueError("no message")
    time_picker = time_picker_builder.build_from_callback(callback_data)
    await bot.edit_message_reply_markup(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        reply_markup=time_picker.get_keyboard(),
    )
