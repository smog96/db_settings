# Python application settings to DB

This lib implement database setting storage with sync and async execution.

## Settings support

### **Types**

+ `int` / `float`
+ `string`
+ `list` / `tuple` / `set`

## Examples

1. Sync settings 

```python
import time
from datetime import datetime

from db_settings.base.settings import SyncSettings
from db_settings.configuration import DBType, SettingsConf


class Settings(SyncSettings):
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
        db_sync_type="sync",
        db_name="settings_lib",
    )


settings = Settings()
print(settings.some_int)
settings.some_int = 12
time.sleep(2)
print(settings.some_int)

```

2. FastAPI support:

```python

from fastapi import FastAPI

from examples.fastapi_example.settings import Settings
from db_settings.fastapi import DbSettingsAPIConfig
from db_settings.fastapi.asyncio import gen_router
from db_settings.fastapi.views import SettingsSchema


# Initialize FastAPII
app = FastAPI()

# Initialize settings
settings = Settings()

SettingsSchema.gen(settings)    # generate pydantic schema

# Configure API settings integration 
DbSettingsAPIConfig.settings_module = settings
DbSettingsAPIConfig.api_prefix = "/api"

# IMPORTANT! Include router after all integrations !
app.include_router(gen_router())

```

## Todo:

1. Redis storage
2. In-memory storage
3. ...
