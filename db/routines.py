from contextlib import asynccontextmanager
import os
from typing import AsyncIterator, Optional

import aiosqlite

_connection: Optional[aiosqlite.Connection] = None


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


async def prepare_database():
    async with get_connection() as conn:
        existing = set()
        for row in await conn.execute_fetchall(
            "SELECT name FROM sqlite_master "
            "WHERE name IN ('wallets', 'transactions')"
        ):
            existing.add(row['name'])

        if existing == {'wallets', 'transactions'}:
            return

        with open(os.path.abspath(__file__ + '/../schema.sql')) as f1, \
            open(os.path.abspath(__file__ + '/../seed.sql')) as f2:
            # NOTE: these must be sequential
            await conn.executescript(f1.read())
            await conn.executescript(f2.read())


async def shutdown_database():
    global _connection

    if _connection:
        await _connection.close()


@asynccontextmanager
async def get_connection() -> AsyncIterator[aiosqlite.Connection]:
    global _connection

    if not _connection:
        _connection = await aiosqlite.connect(
            os.path.abspath(__file__ + '/../../database.sqlite')
        )
        # set to dict_factory to allow pydantic model construction
        _connection.row_factory = dict_factory  # type:ignore
        await _connection.execute('PRAGMA foreign_keys = 1')

    yield _connection
