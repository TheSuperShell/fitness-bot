import datetime
from typing import Annotated

import pytz
from aiogram.types import User as TelegramUser
from pydantic import field_validator
from sqlalchemy import DateTime
from sqlmodel import Column, Field, Relationship, SQLModel

from models.stats import Height, ParamRecord
from utils.time import current_timestamp_utc

type TUser = TelegramUser
TelegramId = Annotated[int, Field()]


class NoUserError(Exception): ...


class UserError(Exception):
    def __init__(self, telegram_id: int) -> None:
        self.telegram_id: int = telegram_id
        super().__init__()

    def __str__(self) -> str:
        return f"[telegram_id: {self.telegram_id}] - {super().__str__()}"

    def __repr__(self) -> str:
        return f"[telegram_id: {self.telegram_id}] - {super().__repr__()}"


class UserNotRegisteredError(UserError): ...


class UserAlreadyExistsError(UserError): ...


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    telegram_id: TelegramId = Field(index=True)
    username: str | None
    first_name: str
    last_name: str | None
    height: Height
    is_active: bool = Field(default=True)
    timezone: str
    created_at: datetime.datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False),
        default_factory=current_timestamp_utc,
    )
    modified_at: datetime.datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), nullable=False, onupdate=current_timestamp_utc
        ),
        default_factory=current_timestamp_utc,
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

    @field_validator("timezone", mode="after")
    @classmethod
    def validate_timezone(cls, value: str) -> str:
        if value not in pytz.all_timezones_set:
            raise ValueError(f"timezone {value} if not a valid timezone")
        return value

    def timestamp_in_users_timezone(
        self, timestamp: datetime.datetime
    ) -> datetime.datetime:
        return timestamp.astimezone(pytz.timezone(self.timezone))
