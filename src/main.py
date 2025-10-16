import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated

from aiogram.methods import TelegramMethod
from aiogram.types import Update
from fastapi import Depends, FastAPI, Header, HTTPException, Request, status

from .bot import setup, shutdown_event, startup_event
from .config import config
from .logger import get_logger

dp, bot = setup()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await startup_event(dp, bot)
    yield
    await shutdown_event(dp)


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def hello_world() -> str:
    return "Hello, World!"


@app.post(config.webhook_path)
async def webhook_post(
    request: Request,
    logger: Annotated[logging.Logger, Depends(get_logger)],
    x_telegram_bot_api_secret_token: Annotated[str | None, Header()] = None,
) -> dict:
    logger.info("got post request")
    if x_telegram_bot_api_secret_token != config.webhook_secret:
        logger.warning("unauthorised access")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="used the incorrect webhook secret",
        )
    update: Update = Update.model_validate(await request.json())
    response = await dp.feed_update(bot, update)
    if isinstance(response, TelegramMethod):
        await bot(response)
    return {"ok": True}
