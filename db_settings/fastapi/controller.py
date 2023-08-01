from fastapi import APIRouter, Body, Depends

from db_settings import fastapi
from db_settings.fastapi import DbSettingsAPIConfig, Permissions
from db_settings.fastapi.views import SettingsSchema, DefaultResponse


def gen_router() -> APIRouter:
    def get_all():
        return DbSettingsAPIConfig.settings_module.all()

    def update_settings(
        data: SettingsSchema.schema(optional=True) = Body(),
    ):
        data = data.model_dump(exclude_none=True)
        for k, v in data.items():
            setattr(DbSettingsAPIConfig.settings_module, k, v)
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
