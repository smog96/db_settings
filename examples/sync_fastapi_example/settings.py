from datetime import datetime

from db_settings.base import SettingsBase
from db_settings.configuration import DBType, SettingsConf


class Settings(SettingsBase):
    some_date: datetime = datetime(2020, 1, 2)
    some_string: str = "hello world"
    some_int: int = 1
    some_tuple: tuple = (1, 2, 3)
    config = SettingsConf(
        timeout=1,
        db_type=DBType.pg_psycopg,
        db_host="localhost",
        db_port=5432,
        db_user="postgres",
        db_password="postgres",
        db_sync_type="sync",
        db_name="postgres",
    )
