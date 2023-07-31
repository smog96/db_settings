import asyncio
from datetime import datetime

import pytest

from db_settings.base import AsyncSettingsBase as SettingsBase
from db_settings.configuration import DBType, SettingsConf


class Settings(SettingsBase):
    some_date: datetime = datetime(2020, 1, 2)
    some_string: str = "hello world"
    some_int: int = 1
    some_tuple: tuple = (1, 2, 3)
    config = SettingsConf(
        timeout=1,
        db_type=DBType.postgresql,
        db_host="localhost",
        db_port=5432,
        db_user="postgres",
        db_password="postgres",
        db_sync_type="async",
        db_name="settings_lib",
    )


@pytest.mark.asyncio
async def test_sync_settings():
    settings = Settings()
    value = await settings.get(settings.some_int)
    assert value in (1, 12)
    await settings.set("some_int", 12)
    await asyncio.sleep(2)
    value = await settings.get("some_int")
    assert value == 12
