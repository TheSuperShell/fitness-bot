from aiogram import Router
from aiogram.types import Message
from aiogram.methods.send_message import SendMessage
from aiogram.filters import CommandStart


router = Router(name=__name__)


@router.message(CommandStart())
def start(message: Message) -> SendMessage:
    return message.answer("Hello")
