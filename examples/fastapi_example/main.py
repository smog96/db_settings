from fastapi import FastAPI

from examples.fastapi_example.settings import Settings
from db_settings.fastapi import DbSettingsAPIConfig
from db_settings.fastapi.asyncio import gen_router
from db_settings.fastapi.views import SettingsSchema

app = FastAPI()

settings = Settings()
SettingsSchema.gen(settings)
DbSettingsAPIConfig.settings_module = settings
DbSettingsAPIConfig.api_prefix = "/api"

app.include_router(gen_router())
