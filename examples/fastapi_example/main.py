import random

from fastapi import FastAPI

from examples.fastapi_example.settings import Settings
from db_settings.fastapi import DbSettingsAPIConfig
from db_settings.fastapi.asyncio import gen_router
from db_settings.fastapi.views import SettingsSchema

# Initialize FastAPII
app = FastAPI()

# Initialize settings
settings = Settings()

SettingsSchema.gen(settings)  # generate pydantic schema

# Configure API settings integration
DbSettingsAPIConfig.settings_module = settings
DbSettingsAPIConfig.api_prefix = "/api"

# IMPORTANT! Include router after all integrations !
app.include_router(gen_router())


@app.on_event("startup")
async def on_start():
    print(await settings.aall())


@app.on_event("startup")
def sync_on_start():
    print(settings.all())
    print(settings.some_int)


@app.get("/test_url")
async def get() -> dict:
    some_rnd = random.randint(0, 20000)
    await settings.aset("some_int", some_rnd)
    a = await settings.aget("some_int", force=True)
    return {
        "db_value": a,
        "rnd": some_rnd,
    }
