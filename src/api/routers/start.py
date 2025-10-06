from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.methods import SendMessage
from aiogram.types import Message

from services.user import get_user

router = Router(name=__name__)


@router.message(CommandStart())
def start(message: Message) -> SendMessage:
    user = get_user(message)
    return message.answer(f"Hello, {user.full_name}")
