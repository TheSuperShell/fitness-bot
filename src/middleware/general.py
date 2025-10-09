from logging import Logger

from aiogram.methods.send_message import SendMessage
from aiogram.types import ErrorEvent


async def other_exceptions(event: ErrorEvent, logger: Logger) -> SendMessage | None:
    logger.critical(f"unhandeled error: {event.exception}")
    return event.update.message.answer("Unkown error") if event.update.message else None
