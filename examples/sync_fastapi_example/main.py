import time

from fastapi import FastAPI

from examples.sync_fastapi_example.settings import Settings
from db_settings.fastapi import DbSettingsAPIConfig
from db_settings.fastapi.sync import gen_router
from db_settings.fastapi.views import SettingsSchema

# Initialize FastAPII
app = FastAPI()

# Initialize settings
settings = Settings()

SettingsSchema.gen(settings)  # generate pydantic schema

# Configure API settings integration
DbSettingsAPIConfig.settings_module = settings
DbSettingsAPIConfig.api_prefix = "/api/"

# IMPORTANT! Include router after all integrations !
app.include_router(gen_router())

settings.some_string = "Sync settings example"
print(settings.all())
print(settings.some_int)
