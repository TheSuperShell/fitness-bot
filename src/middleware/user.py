from logging import Logger

from aiogram.methods.send_message import SendMessage
from aiogram.types import ErrorEvent

from ..models.user import UserNotRegisteredError


async def no_user_error(event: ErrorEvent, logger: Logger) -> SendMessage | None:
    logger.error("no user found")
    return (
        event.update.message.answer("ERROR: no user found")
        if event.update.message
        else None
    )


async def user_not_registered_error(
    event: ErrorEvent, logger: Logger
) -> SendMessage | None:
    if not isinstance(event.exception, UserNotRegisteredError):
        return
    logger.warning(f"user {event.exception.telegram_id} is not registered")
    return (
        event.update.message.answer(
            "We could not find your user\. Please register using /start command"  # pyright: ignore[reportInvalidStringEscapeSequence]
        )
        if event.update.message
        else None
    )
