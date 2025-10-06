from aiogram.types import User as TelegramUser
from sqlmodel import Field, SQLModel

type TUser = TelegramUser
type TelegramId = int


class NoUserError(Exception): ...


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    telegram_id: TelegramId = Field(index=True)
    username: str | None
    first_name: str
    last_name: str | None

    @property
    def full_name(self) -> str:
        return f"{self.first_name}" + (f" {self.last_name}" if self.last_name else "")
