import sys
from typing import Any

from psycopg_pool import AsyncConnectionPool, ConnectionPool

from db_settings.db_drivers.base import BaseDriver
from db_settings.db_drivers.postgresql import querysets as qs
from db_settings.db_drivers.temps import postgres_connection_string
from db_settings.log import logger

try:
    import psycopg
except ImportError:
    logger.exception("Psycopg 3 module important to use postgresql.")
    raise sys.exit(1)


class PostgresqlDriver(BaseDriver):
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

    def _execute(self, query: str) -> psycopg.Cursor:
        with self.pool.connection() as conn:
            res = conn.execute(query)
            return res

    async def _aexecute(self, query: str) -> psycopg.AsyncCursor:
        async with self.apool.connection() as conn:
            return await conn.execute(query)

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
        await self.execute(query)

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
        cur = await self.execute(query)
        res = await cur.fetchone()
        return res[0]

    def all(self) -> dict[str, Any]:
        query = qs.SELECT_ALL.substitute()
        cur = self.execute(query)
        return cur.fetchall()

    async def aall(self) -> dict[str, Any]:
        query = qs.SELECT_ALL.substitute()
        cur = await self.execute(query)
        return cur.fetchall()

    def init(self):
        try:
            return self._check_table_exist()
        except psycopg.errors.UndefinedTable:
            self._create_table()
            return {}

    def _check_table_exist(self) -> dict[str, Any]:
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
