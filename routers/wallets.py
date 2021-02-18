import logging
from typing import List
import aiosqlite

from fastapi import APIRouter, Response, Path
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Query

from db.routines import get_connection
from schemas import WalletIn, WalletOut

router = APIRouter(prefix='/wallets')


@router.get('/', response_model=List[WalletOut])
async def list_wallets():
    async with get_connection() as conn:
        return await conn.execute_fetchall('SELECT * FROM wallets')


@router.post('/', response_model=int, status_code=201)
async def create_wallet(wallet: WalletIn):
    async with get_connection() as conn:
        resp = await conn.execute_insert(
            'INSERT INTO wallets (name, balance) VALUES (:name, :balance)',
            wallet.dict()
        )
        await conn.commit()
        return resp['last_insert_rowid()']


@router.put('/{id}/', response_class=Response, status_code=204)
async def rename_wallet(id: int = Path(...),
                        name: str = Query(..., min_length=1, max_length=64)):
    async with get_connection() as conn:
        await conn.execute(
            'UPDATE wallets SET name = ? WHERE id = ?',
            (name, id)
        )
        await conn.commit()


@router.delete('/{id}/', response_class=Response, status_code=204, responses={409: {'model': str}})
async def delete_wallet(id: int = Path(..., gt=1)):
    """_Our_ wallet can't be deleted."""
    async with get_connection() as conn:
        try:
            await conn.execute('DELETE FROM wallets WHERE id = ?', (id, ))
            await conn.commit()
        except aiosqlite.IntegrityError as e:
            await conn.rollback()
            logging.exception(e)
            raise HTTPException(409)
