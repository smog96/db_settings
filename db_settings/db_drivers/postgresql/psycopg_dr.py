import asyncio
import sys
import time
from typing import Any

from psycopg import OperationalError
from psycopg_pool import AsyncConnectionPool, ConnectionPool

from db_settings.db_drivers.base import BaseDriver
from db_settings.db_drivers.postgresql import querysets as qs
from db_settings.db_drivers.temps import postgres_connection_string
from db_settings.exceptions import DBError
from db_settings.log import logger

try:
    import psycopg
except ImportError:
    logger.exception("Psycopg 3 module important to use postgresql.")
    raise sys.exit(1)


class PsycopgDriver(BaseDriver):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conn_string = self._conn_str()
        if self._is_async:
            self.apool: AsyncConnectionPool = AsyncConnectionPool(
                self.conn_string
            )
        self.pool: ConnectionPool = ConnectionPool(self.conn_string)

    def _conn_str(self):
        db = self._db
        return postgres_connection_string.substitute(
            user=db.db_user,
            password=db.db_password,
            host=db.db_host,
            port=db.db_port,
            name=db.db_name,
        )

    def execute(self, query: str, commit: bool = True) -> psycopg.Cursor:
        failure_counter = 0
        with self.pool.connection() as conn:
            while True:
                try:
                    res = conn.execute(query)
                    if commit:
                        conn.commit()
                    break
                except OperationalError:
                    failure_counter += 1
                    time.sleep(0.2)
                    if failure_counter > 5:
                        raise DBError
        return res

    async def aexecute(
        self, query: str, commit: bool = True
    ) -> psycopg.AsyncCursor:
        failure_counter = 0
        async with self.apool.connection() as conn:
            while True:
                try:
                    res = await conn.execute(query)
                    if commit:
                        await conn.commit()
                    break
                except OperationalError:
                    failure_counter += 1
                    await asyncio.sleep(0.2)
                    if failure_counter > 5:
                        raise DBError
            return res

    def set(self, key: str, value: str):
        logger.debug(f"Update {key} to {value} in DB.")
        query = qs.INSERT_OR_UPDATE.substitute(
            table_name=self._db.table_name,
            key=key,
            value=value,
            service_name=self._db.service_name,
        )
        return self.execute(query)

    async def aset(self, key: str, value: str):
        logger.debug(f"Async update {key} to {value} in DB.")
        query = qs.INSERT_OR_UPDATE.substitute(
            table_name=self._db.table_name,
            key=key,
            value=value,
            service_name=self._db.service_name,
        )
        await self.aexecute(query)

    def fetch(self, key: str) -> Any:
        query = qs.SELECT_ONE.substitute(
            table_name=self._db.table_name,
            key=key,
            service_name=self._db.service_name,
        )
        cur = self.execute(query)
        return cur.fetchone()

    async def afetch(self, key: str) -> Any:
        query = qs.SELECT_ONE.substitute(
            table_name=self._db.table_name,
            key=key,
            service_name=self._db.service_name,
        )
        cur = await self.aexecute(query)
        res = await cur.fetchone()
        return res[0]

    def all(self) -> list[dict[str, Any]]:
        query = qs.SELECT_ALL.substitute()
        cur = self.execute(query)
        return cur.fetchall()

    async def aall(self) -> list[dict[str, Any]]:
        query = qs.SELECT_ALL.substitute()
        cur = await self.aexecute(query)
        return await cur.fetchall()

    def init(self):
        try:
            self._chekc_db()
            return self._check_table_exist()
        except psycopg.errors.UndefinedTable:
            self._create_table()
            return {}

    def _chekc_db(self):
        recovery_query = qs.RECOVERY_STATE.substitute()
        cur = self.execute(recovery_query)
        logger.debug(f"Recovery state: {cur.fetchall()}")
        transaction_ro_query = qs.DEFAULT_TRANSACTION_RO.substitute()
        cur = self.execute(transaction_ro_query)
        logger.debug(f"transaction_ro: {cur.fetchall()}")

    def _check_table_exist(self) -> dict[str, Any]:
        query = qs.SELECT_ALL.substitute(
            table_name=self._db.table_name,
            service_name=self._db.service_name,
        )
        cur = self.execute(query)
        exists = cur.fetchall()
        logger.info(f"Table exist: {exists}")
        return dict(exists)

    def _create_table(self):
        query = qs.CREATE_TABLE.substitute(table_name=self._db.table_name)
        self.execute(query)
