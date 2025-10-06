from aiogram.types import Message
from aiogram.types import User as TUser

from models.user import NoUserError


def get_user(message: Message) -> TUser:
    if not message.from_user:
        raise NoUserError
    return message.from_user
