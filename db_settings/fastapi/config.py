from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine

from fastapi import Depends

from db_settings.fastapi.views import TBaseSettings


@dataclass
class _DbSettingsAPIConfig:
    settings_module: TBaseSettings = None
    api_prefix: str = "/"
    tags: list[str] = field(default_factory=lambda: ["DB settings"])
    dependencies: list = field(default_factory=lambda: [])
    route_args: dict = field(default_factory=lambda: {})


DbSettingsAPIConfig = _DbSettingsAPIConfig()


def _test_():
    return 10


def default_allow_all(dep: int = Depends(_test_)) -> bool:
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
