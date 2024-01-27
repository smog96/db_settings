from fastapi import APIRouter, Body, Depends, Query

from db_settings import fastapi
from db_settings.fastapi import DbSettingsAPIConfig, Permissions
from db_settings.fastapi.views import DefaultResponse, SettingsSchema


def gen_router(router: APIRouter | None = None) -> APIRouter:
    if router is None:
        if (
            len(fastapi.DbSettingsAPIConfig.api_prefix) > 1
            and fastapi.DbSettingsAPIConfig.api_prefix[-1] == "/"
        ):
            postfix = "db_settings"
        else:
            postfix = "/db_settings"
        router = APIRouter(
            prefix=fastapi.DbSettingsAPIConfig.api_prefix + postfix,
            dependencies=fastapi.DbSettingsAPIConfig.dependencies,
            tags=fastapi.DbSettingsAPIConfig.tags,
            **fastapi.DbSettingsAPIConfig.route_args
        )

    def get_all(force: bool = Query(default=False)):
        return DbSettingsAPIConfig.settings_module.all(force=force)

    def update_settings(
        data: SettingsSchema.schema(optional=True) = Body(),
    ):
        data = data.model_dump(exclude_none=True)
        for k, v in data.items():
            setattr(DbSettingsAPIConfig.settings_module, k, v)
        return DefaultResponse

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
