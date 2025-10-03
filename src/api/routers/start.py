from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.methods.send_message import SendMessage
from aiogram.types import Message

router = Router(name=__name__)


@router.message(CommandStart())
def start(message: Message) -> SendMessage:
    return message.answer("Hello")
