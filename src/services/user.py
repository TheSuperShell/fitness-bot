from logging import Logger

from aiogram.types import Message
from sqlmodel import select

from db.session import SessionMaker
from models.stats import Height
from models.user import NoUserError, TUser, User, UserAlreadyExistsError


def get_telegram_user(message: Message) -> TUser:
    if not message.from_user:
        raise NoUserError
    return message.from_user


async def get_user_if_exists(
    telegram_user: TUser, session_maker: SessionMaker
) -> User | None:
    async with session_maker() as session:
        res = await session.execute(
            select(User).where(User.telegram_id == telegram_user.id)
        )
        return res.scalar_one_or_none()


async def create_user(
    telegram_user: TUser, sessionmaker: SessionMaker, logger: Logger, height: Height
) -> User:
    async with sessionmaker() as session:
        res = await session.execute(
            select(User).where(
                (User.telegram_id == telegram_user.id) & (User.is_active)
            )
        )
        user_or_none = res.scalar_one_or_none()
        if user_or_none:
            raise UserAlreadyExistsError(telegram_id=telegram_user.id)
        user = User(
            telegram_id=telegram_user.id,
            username=telegram_user.username,
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name,
            height=height,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        logger.info(f"created a new user with id {user.telegram_id}")
    return user
