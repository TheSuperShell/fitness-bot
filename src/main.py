import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import ExceptionTypeFilter
from magic_filter import F

from api.routers import general_router, start_router, stats_router, test_router
from config import config
from db.session import async_engine, db_startup, session_maker
from logger import get_logger, setup_logging
from middleware.general import other_exceptions
from middleware.user import no_user_error, user_not_registered_error
from models.user import NoUserError, UserNotRegisteredError


async def startup_event(dispatcher: Dispatcher) -> None:
    dispatcher["log_listener"] = setup_logging()
    dispatcher["logger"] = get_logger()
    dispatcher["session_maker"] = session_maker
    await db_startup()
    dispatcher["logger"].info("startup completed")


async def shutdown_event(dispatcher: Dispatcher) -> None:
    dispatcher["log_listener"].stop()
    await async_engine.dispose()
    dispatcher["logger"].info("shutown completed")


async def main() -> None:
    dp = Dispatcher()
    dp.startup.register(startup_event)
    dp.shutdown.register(shutdown_event)
    dp.include_routers(general_router, start_router, stats_router, test_router)
    dp.error.register(
        no_user_error,
        ExceptionTypeFilter(NoUserError),
        F.update.message,
    )
    dp.error.register(
        user_not_registered_error,
        ExceptionTypeFilter(UserNotRegisteredError),
        F.update.message,
    )
    dp.error.register(other_exceptions)
    bot = Bot(
        token=config.bot_api_key,
        default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2),
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
