from datetime import datetime
from typing import Any

from asyncer import syncify

from db_settings.configuration import DRIVER_MAPPING, SettingsConf
from db_settings.db_drivers.base import TBaseDBDriver
from db_settings.exceptions import DBError
from db_settings.time.converts import to_str, to_time


class SettingsBase:
    __slots__ = [
        "config",
        "_values",
        "_ttls",
        "_initialized",
        "_db_cls",
        "_is_async",
    ]

    __allowed_types__ = (
        list,
        tuple,
        set,
        int,
        str,
        datetime,
        bool,
        float,
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
        self._is_async: bool = self.config.db_sync_type

        self.root_validator()
        self._init()
        self._initialized = True

    def root_validator(self):
        for key in self.__annotations__.values():
            if key not in self.__allowed_types__:
                raise ValueError(f"Type {key} not supported yet.")

    async def aall(self, force: bool = False) -> dict:
        vals = self.__annotations__.keys()
        res = {}
        for k in vals:
            res[k] = await self.aget(k, force=force)
        return res

    async def aget(self, item: Any, force: bool = False):
        ttl = self._ttls.get(item, None)
        try:
            if force or (
                ttl
                and self.config
                and (datetime.utcnow() - ttl).seconds > self.config.timeout
            ):
                value = await self._afetch_value(key=item)
                self._ttls.setdefault(item, datetime.utcnow())
                return self._value_to_type(name=item, value=value)
        except (TypeError, DBError):
            pass
        value = self._values.get(item)
        return self._value_to_type(name=item, value=value)

    async def aset(self, item: Any, value: Any):
        await self._aupdate_value(key=item, value=value)

    async def _aupdate_value(self, key: str, value: Any):
        await self._db_cls.aset(key=key, value=value)

    async def _afetch_value(self, key: str):
        return await self._db_cls.afetch(key=key)

    def all(self, force: bool = False) -> dict:
        res = {}
        for key in self.__annotations__.keys():
            if force:
                try:
                    value = self.get(key)
                except (TypeError, IndexError, ValueError):
                    value = getattr(self, key)
            else:
                value = getattr(self, key)
            res[key] = value
        return res

    def _init(self):
        exists_values = self._db_cls.init()

        self._values = {
            key: exists_values.get(key, getattr(self, key, None))
            for key in self.__annotations__.keys()
        }
        _n = datetime.utcnow()
        self._ttls = {k: _n for k in self.__annotations__.keys()}

    def _update_value(self, key: str, value: Any):
        if isinstance(self.__annotations__.get(key), datetime):
            value = to_str(value, fmt=self.config.datetime_fmt)
        self._db_cls.set(key=key, value=value)

    def get(self, key: str) -> Any:
        value = self._db_cls.fetch(key=key)
        value = value[0]
        self._ttls.setdefault(key, datetime.utcnow())
        return self._value_to_type(key, value)

    def __setattr__(self, __name: str, __value: Any) -> None:
        if __name in (
            "config",
            "aset",
            "aget",
            "set",
            "get",
            "root_validator",
            "all",
            "aall",
        ) or __name.startswith("_"):
            return super().__setattr__(__name, __value)
        return self._update_value(__name, __value)

    def __getattr__(self, item: str):
        ttl = self._ttls.get(item, None)
        try:
            if (
                ttl
                and self.config
                and (datetime.utcnow() - ttl).seconds > self.config.timeout
            ):
                return self.get(key=item)
        except (TypeError, DBError):
            pass
        return self._value_to_type(item, self._values.get(item))

    def __getattribute__(self, __name: str) -> Any:
        if (
            __name
            in (
                "config",
                "aset",
                "aget",
                "set",
                "get",
                "root_validator",
                "all",
                "aall",
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
        elif type_ is datetime:
            value = to_time(value, fmt=self.config.datetime_fmt)
        elif type_ in (list, tuple, set) and isinstance(value, str):
            value = ast.literal_eval(value)
        elif type_ in [bool]:
            if value in (1, 1.0, "true", "True", "y", "yes"):
                value = True
            else:
                value = False
        elif isinstance(type(value), type_) is False:
            value = type_(value)
        else:
            pass
        return value
