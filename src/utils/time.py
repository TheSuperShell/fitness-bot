import datetime
import time

import requests
from aiogram.types import Location

from ..config import config


class TimezoneApiError(Exception):
    def __init__(self, status_code: str) -> None:
        self.status_code: str = status_code
        super().__init__()

    def __str__(self) -> str:
        return f"status_code: {self.status_code}"


def current_timestamp_utc() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC)


def get_timezone_from_location(location: Location) -> str:
    timestamp = int(time.time())
    url = (
        "https://maps.googleapis.com/maps/api/timezone/json"
        f"?location={location.latitude},{location.longitude}"
        f"&timestamp={timestamp}"
        f"&key={config.google_timezone_api_key}"
    )
    response = requests.get(url)
    if response.status_code != 200:
        raise TimezoneApiError(response.reason)
    data = response.json()
    if data["status"] != "OK":
        raise TimezoneApiError(data["status"])
    return data["timeZoneId"]
