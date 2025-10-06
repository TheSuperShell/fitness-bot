from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from config import config

type SessionMaker = async_sessionmaker[AsyncSession]

async_engine = create_async_engine(config.db_url, echo=True)
session_maker = async_sessionmaker(async_engine, expire_on_commit=False)


async def db_startup() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
