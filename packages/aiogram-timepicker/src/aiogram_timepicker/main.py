import datetime
from typing import Annotated

import pytz
from aiogram import F
from aiogram.filters.callback_data import CallbackData, CallbackQueryFilter
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.magic_filter import MagicFilter
from pydantic import BaseModel, Field

Hour = Annotated[int, Field(ge=0, le=23)]
Minute = Annotated[int, Field(ge=0, le=59)]


class TimeQuery(CallbackData, prefix="time"):
    name: str
    hour: Hour
    minute: Minute
    ok: bool = Field(default=False)

    def get_datetime_today_utc(self, timezone: str = "UTC") -> datetime.datetime:
        """get the datetime from the selected hour and minute converted
        from the sepcified timezone into UTC

        Args:
            timezone (str, optional): timezone of the selected time. Defaults to "UTC".

        Returns:
            datetime.datetime: datetime object for the selected time
            (the date is `today` in local timezone) converted into UTC
        """
        tz = pytz.timezone(timezone)
        dt = datetime.datetime.combine(
            datetime.datetime.now(tz).date(), datetime.time(self.hour, self.minute)
        )
        dt_local = tz.localize(dt)
        return dt_local.astimezone(pytz.UTC)


class TimePicker(BaseModel, frozen=True):
    """
    This is a timepicker generator class with a local (timezone specific) hour
    and minute
    """

    name: str
    hour: Hour
    minute: Minute

    def _no_action(self) -> TimeQuery:
        return TimeQuery(name=self.name, hour=self.hour, minute=self.minute)

    def _increase_hour(self) -> TimeQuery:
        return TimeQuery(
            name=self.name,
            hour=self.hour + 1 if self.hour < 23 else 0,
            minute=self.minute,
        )

    def _decrease_hour(self) -> TimeQuery:
        return TimeQuery(
            name=self.name,
            hour=self.hour - 1 if self.hour > 0 else 23,
            minute=self.minute,
        )

    def _increase_minute(self) -> TimeQuery:
        return TimeQuery(
            name=self.name,
            hour=self.hour,
            minute=self.minute + 1 if self.minute < 59 else 0,
        )

    def _decrease_minute(self) -> TimeQuery:
        return TimeQuery(
            name=self.name,
            hour=self.hour,
            minute=self.minute - 1 if self.minute > 0 else 59,
        )

    def get_keyboard(self) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="↑", callback_data=self._increase_hour().pack()
                    ),
                    InlineKeyboardButton(
                        text="↑", callback_data=self._increase_minute().pack()
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text=str(self.hour), callback_data=self._no_action().pack()
                    ),
                    InlineKeyboardButton(
                        text=str(self.minute), callback_data=self._no_action().pack()
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="↓", callback_data=self._decrease_hour().pack()
                    ),
                    InlineKeyboardButton(
                        text="↓", callback_data=self._decrease_minute().pack()
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="Ok",
                        callback_data=TimeQuery(
                            name=self.name, hour=self.hour, minute=self.minute, ok=True
                        ).pack(),
                    )
                ],
            ]
        )


class TimePickerBuilder(BaseModel):
    name: str

    def filter(self, rule: MagicFilter | None = None) -> CallbackQueryFilter:
        final_rule: MagicFilter = F.name == self.name
        if rule:
            final_rule = (final_rule) & (rule)
        return TimeQuery.filter(final_rule)

    def ok_filter(self) -> CallbackQueryFilter:
        return TimeQuery.filter((F.name == self.name) & (F.ok))

    def build_from_timestamp_tz(self, timestamp: datetime.datetime) -> TimePicker:
        """build a timepicker from the timestamp with the local timezone

        Args:
            timestamp (datetime.datetime): timestamp with tz

        Returns:
            TimePicker: TimePicker with the hour and minute from the timestamp
        """
        return TimePicker(name=self.name, hour=timestamp.hour, minute=timestamp.minute)

    def build_from_callback(self, callback_data: TimeQuery) -> TimePicker:
        return TimePicker(
            name=self.name, hour=callback_data.hour, minute=callback_data.minute
        )
