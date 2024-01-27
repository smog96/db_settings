from typing import Any

import asyncer
import asyncpg

from db_settings.db_drivers.base import BaseDriver
from db_settings.db_drivers.postgresql import querysets as qs
from db_settings.log import logger


class AsyncPgDriver(BaseDriver):
    """
    SingleTone class for cleaner connection pool management
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pool = None

    async def create_pool(self):
        self.pool: asyncpg.Pool = await asyncpg.create_pool(
            database=self._db.db_name,
            user=self._db.db_user,
            host=self._db.db_host,
            password=self._db.db_password,
            port=self._db.db_port,
            max_inactive_connection_lifetime=3,
            min_size=1,
        )

    async def shutdown(self):
        """
        Attempt to gracefully close all connections in the pool
        `pool.terminate` is redundant because it's called automatically if
        any errors occur
        """
        await self.pool.close()

    def acquire_connection(self):
        return self.pool.acquire()

    """
        async with DB_CLIENT.acquire_connection() as con:
        return await con.fetch(
            templates.compact_select_by_status.substitute(status="applied")
        )
    """

    def _execute(self, query: str, commit: bool = True):
        return asyncer.syncify(self._aexecute)(query=query, commit=commit)

    async def _aexecute(self, query: str, commit: bool = True):
        async with self.acquire_connection() as conn:
            res = await conn.execute(query)
            if commit:
                await conn.commit()
            return res

    def fetch(self, key: str) -> Any:
        return asyncer.syncify(self.afetch)(key)

    async def afetch(self, key: str) -> Any:
        query = qs.SELECT_ONE.substitute(
            table_name=self._db.table_name,
            key=key,
            service_name=self._db.service_name,
        )
        cur = await self.execute(query)
        res = await cur.fetchone()
        return res[0]

    def set(self, key: str, value: Any):
        return asyncer.syncify(self.aset)(key, value)

    async def aset(self, key: str, value: Any):
        logger.debug(f"Async update {key} to {value} in DB.")
        query = qs.INSERT_OR_UPDATE.substitute(
            table_name=self._db.table_name,
            key=key,
            value=value,
            service_name=self._db.service_name,
        )
        await self.execute(query)

    def init(self) -> dict | None:
        try:
            return self._check_table_exist()
        except Exception as exc:
            logger.error(exc)
            self._create_table()
            return {}

    def _check_table_exist(self):
        query = qs.SELECT_ALL.substitute(
            table_name=self._db.table_name,
            service_name=self._db.service_name,
        )
        cur = self._execute(query)
        exists = cur.fetchall()
        logger.info(f"Table exist: {exists}")
        return dict(exists)

    def _create_table(self):
        query = qs.CREATE_TABLE.substitute(table_name=self._db.table_name)
        self._execute(query)
