from datetime import timedelta
from typing import Literal

from db_settings.db_drivers import PostgresqlDriver, RedisDriver
from db_settings.db_drivers.datas import DbData
from db_settings.time.defaults import STDF

DRIVER_MAPPING = {
    "postgresql": PostgresqlDriver,
    "redis": RedisDriver,
}


class _DBType:
    postgresql: Literal["postgresql"] = "postgresql"
    redis: Literal["redis"] = "redis"

    def __getattribute__(self, __name: str) -> str:
        return super().__getattribute__(__name)


DBType = _DBType()


class SettingsConf:
    def __init__(
        self,
        timeout: int | timedelta,
        db_type: Literal["postgresql", "redis"] | DBType,
        db_sync_type: Literal["async", "sync"],
        db_host: str,
        db_port: int,
        db_user: str,
        db_password: str,
        db_name: str,
        service_name: str = "default",
        table_name: str = "settings_store",
        datetime_fmt: str = STDF,
    ) -> None:
        if isinstance(timeout, timedelta):
            self.timeout = timeout.seconds
        else:
            self.timeout = timeout

        self.db: DbData = DbData(
            db_host=db_host,
            db_port=db_port,
            db_user=db_user,
            db_password=db_password,
            db_name=db_name,
            table_name=table_name,
            service_name=service_name,
        )
        self.db_sync_type = db_sync_type == "async"
        self.db_type = db_type
        self.datetime_fmt = datetime_fmt
