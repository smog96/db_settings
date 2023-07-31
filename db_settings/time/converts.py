from datetime import datetime

from db_settings.time.defaults import STDF


def to_str(time: str | datetime, fmt: str = STDF) -> str:
    if isinstance(time, str):
        return time
    return datetime.strftime(time, fmt)


def to_time(string: str | datetime, fmt: str = STDF) -> datetime:
    if isinstance(string, str):
        return datetime.strptime(string, fmt)
    return string
