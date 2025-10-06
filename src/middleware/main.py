from logging import Logger

from aiogram.methods.send_message import SendMessage
from aiogram.types import ErrorEvent


async def no_user_error(event: ErrorEvent, logger: Logger) -> SendMessage | None:
    logger.critical("no user found")
    return (
        event.update.message.answer("ERROR: no user found")
        if event.update.message
        else None
    )
