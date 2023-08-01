from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine, Optional

from db_settings.fastapi.views import TBaseSettings


@dataclass
class _DbSettingsAPIConfig:
    settings_module: TBaseSettings = None
    api_prefix: str = "/"
    dependencies: list = field(default_factory=lambda: [])
    route_args: dict = field(default_factory=lambda: {})


DbSettingsAPIConfig = _DbSettingsAPIConfig()


def default_allow_all() -> bool:
    return True


@dataclass
class _Permissions:
    read_func: list[Callable[..., Coroutine[Any, Any, Any]]] = field(
        default_factory=lambda: [default_allow_all]
    )
    write_func: list[Callable[..., Coroutine[Any, Any, Any]]] = field(
        default_factory=lambda: [default_allow_all]
    )


Permissions = _Permissions()
