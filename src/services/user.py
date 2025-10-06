from aiogram.types import Message

from models.user import NoUserError


def get_user_id(message: Message) -> int:
    if not message.from_user:
        raise NoUserError
    return message.from_user.id
