import time
from datetime import datetime

from db_settings.base.settings import SyncSettings
from db_settings.configuration import DBType, SettingsConf


class Settings(SyncSettings):
    some_date: datetime = datetime(2020, 1, 2)
    some_string: str = "hello world"
    some_int: int = 1
    some_tuple: tuple = (1, 2, 3)
    # Dict type not supported. Raise ValueError in root validation
    some_dict: dict = {"a": 10, "b": 12.0}
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
    print(settings.some_int)
    settings.some_int = 15
    time.sleep(2)
    print(settings.some_int)


run()
