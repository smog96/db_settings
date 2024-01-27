from abc import abstractmethod
from typing import Any, TypeVar

from db_settings.db_drivers.datas import DbData


class BaseDriver:
    def __init__(self, is_async: bool, db: DbData):
        self._is_async = is_async
        self._db = db

    @abstractmethod
    def _execute(self, query: str, commit: bool = True):
        raise NotImplementedError

    @abstractmethod
    async def _aexecute(self, query: str, commit: bool = True):
        raise NotImplementedError

    @abstractmethod
    def fetch(self, key: str) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def afetch(self, key: str) -> Any:
        raise NotImplementedError

    @abstractmethod
    def set(self, key: str, value: Any):
        raise NotImplementedError

    @abstractmethod
    async def aset(self, key: str, value: Any):
        raise NotImplementedError

    @abstractmethod
    def init(self) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    def _check_table_exist(self):
        raise NotImplementedError

    @abstractmethod
    def _create_table(self):
        raise NotImplementedError


TBaseDBDriver = TypeVar("TBaseDBDriver", bound=BaseDriver)
