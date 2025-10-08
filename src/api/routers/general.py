from logging import Logger

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.methods import SendMessage
from aiogram.types import Message

router = Router(name=__name__)


@router.message(Command("cancel"))
@router.message(F.text.casefold() == "cacnel")
async def cancel_add_record_state(
    message: Message, state: FSMContext, logger: Logger
) -> SendMessage | None:
    current_state = await state.get_state()
    if current_state is None:
        return None
    await state.clear()
    logger.info(f"Canceled state {current_state!r}")
    return message.answer("Cancleled")
