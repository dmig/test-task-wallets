import logging
from typing import List

import aiosqlite
from fastapi import APIRouter, Response, Path, Body, Query
from fastapi.exceptions import HTTPException

from db.routines import get_connection
from schemas import CommissionPayer, TransactionIn, TransactionOut

router = APIRouter(prefix='/transactions')


OUR_WALLET_ID=1
COMMISSION = 0.015


@router.get('/', response_model=List[TransactionOut])
async def list_transactions(page: int = Query(0, ge=0),
                            size: int = Query(10, gt=0, lte=100)):
    async with get_connection() as conn:
        return await conn.execute_fetchall(
            'SELECT rowid, * FROM transactions ORDER BY created_at DESC '
            'LIMIT ? OFFSET ?',
            (page, page * size)
        )


@router.post('/', response_class=Response, status_code=201, responses={409: {'model': str}})
async def create_transaction(transaction: TransactionIn = Body(...),
                             cp: CommissionPayer = Body(CommissionPayer.sender, alias='commission',
                                                        title='who pays commission: sender, receiver or both')):
    transactions = [transaction]
    wallets = []

    if cp == CommissionPayer.both:
        commission = TransactionIn(from_id=transaction.from_id,
                                   to_id=OUR_WALLET_ID,
                                   amount=transaction.amount * COMMISSION / 2,
                                   comment='0.75% commission')
        transactions.append(commission)
        transactions.append(commission.copy(update={'from_id': transaction.to_id}))

        delta_amount_f = transaction.amount + commission.amount
        wallets.append((-delta_amount_f, transaction.from_id))
        wallets.append((transaction.amount - commission.amount, transaction.to_id))
        wallets.append((2 * commission.amount, OUR_WALLET_ID))

    elif cp == CommissionPayer.receiver:
        commission = TransactionIn(from_id=transaction.to_id,
                                   to_id=OUR_WALLET_ID,
                                   amount=transaction.amount * COMMISSION,
                                   comment='1.5% commission')
        transactions.append(commission)

        delta_amount_f = transaction.amount
        wallets.append((-delta_amount_f, transaction.from_id))
        wallets.append((transaction.amount - commission.amount, transaction.to_id))
        wallets.append((commission.amount, OUR_WALLET_ID))
    else:
        commission = TransactionIn(from_id=transaction.from_id,
                                   to_id=OUR_WALLET_ID,
                                   amount=transaction.amount * COMMISSION,
                                   comment='1.5% commission')
        transactions.append(commission)

        delta_amount_f = transaction.amount + commission.amount
        wallets.append((-delta_amount_f, transaction.from_id))
        wallets.append((transaction.amount, transaction.to_id))
        wallets.append((commission.amount, OUR_WALLET_ID))

    async with get_connection() as conn:
        try:
            await conn.execute('BEGIN')

            balance = await conn.execute_fetchall(
                'SELECT balance FROM wallets WHERE id = ?',
                (transaction.from_id, )
            )
            if not balance:
                raise HTTPException(409, 'Invalid wallet')

            if balance[0]['balance'] < delta_amount_f:  # type:ignore
                raise HTTPException(409, 'Insufficent funds')

            for tr in transactions:
                await conn.execute_insert(
                    'INSERT INTO transactions (from_id, to_id, amount, comment) '
                    'VALUES (:from_id, :to_id, :amount, :comment)',
                    tr.dict()
                )
            for wp in wallets:
                await conn.execute_insert(
                    'UPDATE wallets SET balance = balance + ? WHERE id = ?',
                    wp
                )
            await conn.commit()
        except HTTPException:
            await conn.rollback()
            raise
        except aiosqlite.IntegrityError as e:
            await conn.rollback()
            logging.exception(e)
            raise HTTPException(409, 'Invalid wallet')


@router.put('/{id}/', response_class=Response, status_code=204)
async def update_comment(id: int = Path(...),
                         comment: str = Query(..., min_length=1, max_length=64)):
    async with get_connection() as conn:
        await conn.execute(
            'UPDATE transactions SET comment = ? WHERE rowid = ?',
            (comment, id)
        )
        await conn.commit()
