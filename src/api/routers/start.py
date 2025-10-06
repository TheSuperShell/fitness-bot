from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.methods.send_message import SendMessage
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

router = Router(name=__name__)


@router.message(CommandStart())
def start(
    message: Message, session_maker: async_sessionmaker[AsyncSession]
) -> SendMessage:
    return message.answer("Hello")
