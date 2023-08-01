from fastapi import APIRouter, Body, Depends

from db_settings import fastapi
from db_settings.fastapi import DbSettingsAPIConfig, Permissions
from db_settings.fastapi.views import DefaultResponse, SettingsSchema


def gen_router() -> APIRouter:
    async def get_all():
        return await DbSettingsAPIConfig.settings_module.all()

    async def update_settings(
        data: SettingsSchema.schema(optional=True) = Body(),
    ):
        data = data.model_dump(exclude_none=True)
        for k, v in data.items():
            await DbSettingsAPIConfig.settings_module.set(item=k, value=v)
        return DefaultResponse

    router = APIRouter(
        prefix=fastapi.DbSettingsAPIConfig.api_prefix + "/db_settings",
        dependencies=fastapi.DbSettingsAPIConfig.dependencies,
        **fastapi.DbSettingsAPIConfig.route_args
    )

    router.add_api_route(
        "/all",
        get_all,
        response_model=SettingsSchema.schema(),
        dependencies=[Depends(func) for func in Permissions.read_func],
    )

    router.add_api_route(
        "/update",
        update_settings,
        methods=["PUT"],
        response_model=DefaultResponse,
        dependencies=[Depends(func) for func in Permissions.write_func],
    )
    return router
