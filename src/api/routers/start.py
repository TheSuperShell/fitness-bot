from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.methods.send_message import SendMessage
from aiogram.types import Message

from services.user import get_user_id

router = Router(name=__name__)


@router.message(CommandStart())
def start(message: Message) -> SendMessage:
    user_id: int = get_user_id(message)
    return message.answer(f"Hello, {user_id}")
