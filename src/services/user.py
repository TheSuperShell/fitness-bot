from logging import Logger

from aiogram.types import Message
from sqlmodel import select

from db.session import SessionMaker
from models.user import NoUserError, TUser, User


def get_telegram_user(message: Message) -> TUser:
    if not message.from_user:
        raise NoUserError
    return message.from_user


async def get_or_create_user(
    telegram_user: TUser, sessionmaker: SessionMaker, logger: Logger
) -> User:
    async with sessionmaker() as session:
        res = await session.execute(
            select(User).where(User.telegram_id == telegram_user.id)
        )
        user_or_none = res.scalar_one_or_none()
        if user_or_none:
            return user_or_none
        user = User(
            telegram_id=telegram_user.id,
            username=telegram_user.username,
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        logger.info(f"created a new user with id {user.telegram_id}")
    return user
