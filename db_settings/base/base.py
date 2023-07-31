from datetime import datetime
from typing import Any

from db_settings import SettingsConf
from db_settings.configuration import DRIVER_MAPPING
from db_settings.db_drivers.base import TBaseDBDriver
from db_settings.time.converts import to_str, to_time


class _SettingsBase:
    __slots__ = ["config", "_values", "_ttls", "_initialized", "_db_cls"]

    __allowed_types__ = (
        list,
        tuple,
        set,
        int,
        str,
        datetime,
    )

    def __init__(self) -> None:
        self.config: SettingsConf = getattr(self, "config", None)

        if self.config is None:
            raise ValueError("SettingsConf must be initialized")

        self._values: dict[str, Any] = {}
        self._ttls: dict[str, datetime] = {}
        self._initialized: bool = False

        self._db_cls: TBaseDBDriver = DRIVER_MAPPING.get(self.config.db_type)(
            is_async=self.config.db_sync_type,
            db=self.config.db,
        )

        self.root_validator()
        self._init()
        self._initialized = True

    def root_validator(self):
        for key in self.__annotations__.values():
            if key not in self.__allowed_types__:
                raise ValueError(f"Type {key} not supported yet.")

    def _init(self):
        exists_values = self._db_cls.init()

        self._values = {
            key: exists_values.get(key, getattr(self, key, None))
            for key in self.__annotations__.keys()
        }
        _n = datetime.now()
        self._ttls = {k: _n for k in self.__annotations__.keys()}

    def _update_value(self, key: str, value: Any):
        if isinstance(self.__annotations__.get(key), datetime):
            value = to_str(value, fmt=self.config.datetime_fmt)
        self._db_cls.set(key=key, value=value)

    def _fetch_value(self, key: str) -> Any:
        value = self._db_cls.fetch(key=key)[0]
        return self._value_to_type(key, value)

    def __setattr__(self, __name: str, __value: Any) -> None:
        if __name in (
            "config",
            "set",
            "get",
            "root_validator",
        ) or __name.startswith("_"):
            return super().__setattr__(__name, __value)
        return self._update_value(__name, __value)

    def __getattr__(self, item: str):
        ttl = self._ttls.get(item, None)
        try:
            if (
                ttl
                and self.config
                and (datetime.now() - ttl).seconds > self.config.timeout
            ):
                value = self._fetch_value(key=item)
                return value
        except TypeError:
            pass
        return self._value_to_type(item, self._values.get(item))

    def __getattribute__(self, __name: str) -> Any:
        if (
            __name
            in (
                "config",
                "set",
                "get",
                "root_validator",
            )
            or __name.startswith("_")
            or self._initialized is False
        ):
            return super().__getattribute__(__name)
        raise AttributeError

    def _value_to_type(self, name: str, value: Any) -> Any:
        import ast

        type_ = self.__annotations__.get(name)
        if type_ is None or isinstance(value, type_):
            return value
        if type_ is datetime:
            value = to_time(value, fmt=self.config.datetime_fmt)
        if type_ in [list, tuple, set]:
            value = ast.literal_eval(value)
        elif isinstance(type(value), type_) is False:
            value = type_(value)
        else:
            pass
        return value
