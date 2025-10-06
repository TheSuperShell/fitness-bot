import datetime
from typing import Annotated

from aiogram.types import User as TelegramUser
from sqlalchemy import DateTime
from sqlmodel import Column, Field, Relationship, SQLModel

from models.stats import ParamRecord
from utils.time import current_timestamp

type TUser = TelegramUser
TelegramId = Annotated[int, Field()]


class NoUserError(Exception): ...


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    telegram_id: TelegramId = Field(index=True)
    username: str | None
    first_name: str
    last_name: str | None
    is_active: bool = Field(default=True)
    created_at: datetime.datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
        default_factory=current_timestamp,
    )
    modified_at: datetime.datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), nullable=False, onupdate=current_timestamp
        ),
        default_factory=current_timestamp,
    )
    deleted_at: datetime.datetime | None = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True), default=None
    )

    records: list[ParamRecord] = Relationship(
        sa_relationship_kwargs={"lazy": "selectin"}
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name}" + (f" {self.last_name}" if self.last_name else "")
