import time
from datetime import datetime

from db_settings.base.settings import SyncSettings
from db_settings.configuration import DBType, SettingsConf


class Settings(SyncSettings):
    some_date: datetime = datetime(2020, 1, 2)
    some_string: str = "hello world"
    some_int: int = 1
    some_tuple: set = (
        15169,
        13335,
        16509,
        396982,
        31624,
        22612,
        8560,
        14618,
        47846,
        12389,
    )
    some_bool: bool = True
    config = SettingsConf(
        timeout=1,
        db_type=DBType.postgresql,
        db_host="localhost",
        db_port=5432,
        db_user="postgres",
        db_password="postgres",
        db_sync_type="sync",
        db_name="settings_lib",
    )


def run():
    settings = Settings()
    # print(type(settings.some_bool), settings.some_bool)
    print(type(settings.some_tuple), settings.some_tuple)
    settings.some_tuple = (
        15169,
        13335,
        16509,
        396982,
        31624,
        22612,
        8560,
        14618,
        47846,
        12389,
    )
    settings.some_bool = not settings.some_bool
    time.sleep(2)
    # print(type(settings.some_bool), settings.some_bool)
    print(settings.all())
    print(type(settings.some_tuple), settings.some_tuple)


run()
