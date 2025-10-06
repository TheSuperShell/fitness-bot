from logging import Logger

from aiogram.methods.send_message import SendMessage
from aiogram.types import ErrorEvent, Message


async def no_user_error(
    event: ErrorEvent, logger: Logger, message: Message
) -> SendMessage:
    logger.critical("no user found")
    return message.answer("ERROR: no user found")
