from datetime import datetime
from typing import Any

from db_settings.base.base import SettingsBase


class AsyncSettingsBase(SettingsBase):
    async def get(self, item: Any):
        ttl = self._ttls.get(item, None)
        if (
            ttl
            and self.config
            and (datetime.now() - ttl).seconds > self.config.timeout
        ):
            value = await self._fetch_value(key=item)
        else:
            value = self._values.get(item)
        return self._value_to_type(name=item, value=value)

    async def all(self) -> dict:
        vals = self.__annotations__.keys()
        res = {}
        for k in vals:
            res[k] = await self.get(k)
        return res

    async def set(self, item: Any, value: Any, force: bool = False):
        # `force` on WIP
        await self._update_value(key=item, value=value)

    def __setattr__(self, __name: str, __value: Any):
        if __name in (
            "config",
            "set",
            "get",
            "root_validator",
            "all",
        ) or __name.startswith("_"):
            return super().__setattr__(__name, __value)
        raise ValueError(
            "Not use in async settings instance. Use `.set()` instead"
        )

    def __getattr__(self, item: str):
        if item in (
            "config",
            "set",
            "get",
            "root_validator",
            "all",
        ) or item.startswith("_"):
            return super().__getattr__(item)
        return item

    async def _update_value(self, key: str, value: Any):
        await self._db_cls.aset(key=key, value=value)

    async def _fetch_value(self, key: str):
        return await self._db_cls.afetch(key=key)
