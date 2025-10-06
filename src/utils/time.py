import datetime


def current_timestamp() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC)
