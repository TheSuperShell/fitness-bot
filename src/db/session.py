from collections.abc import Awaitable, Callable
from typing import Any

import sqlmodel.ext.asyncio.session
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel

from config import get_db_url

AsyncSession = sqlmodel.ext.asyncio.session.AsyncSession

async_engine = create_async_engine(get_db_url(), echo=True)


async def startup() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def set_session(
    handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
    event: TelegramObject,
    data: dict[str, Any],
) -> Awaitable[Any]:
    async with AsyncSession(async_engine) as session:
        data["session"] = session
        return handler(event, data)
