from logging import Logger

from aiogram.methods.send_message import SendMessage
from aiogram.types import ErrorEvent
from message_loader.main import MessageLoader

from ..models.user import UserNotRegisteredError


async def no_user_error(
    event: ErrorEvent, logger: Logger, message_loader: MessageLoader
) -> SendMessage | None:
    logger.error("no user found")
    return (
        event.update.message.answer(message_loader.render_msg("error_no_user"))
        if event.update.message
        else None
    )


async def user_not_registered_error(
    event: ErrorEvent, logger: Logger, message_loader: MessageLoader
) -> SendMessage | None:
    if not isinstance(event.exception, UserNotRegisteredError):
        return None
    logger.warning(f"user {event.exception.telegram_id} is not registered")
    return (
        event.update.message.answer(
            message_loader.render_msg("warn_user_not_registered")
        )
        if event.update.message
        else None
    )
