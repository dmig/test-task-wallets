from datetime import datetime
from enum import Enum

from typing import Optional
from pydantic import BaseModel
from pydantic.fields import Field
from pydantic.types import confloat


class WalletIn(BaseModel):
    name: str
    balance: float = Field(0.0)

class WalletOut(WalletIn):
    id: int

class TransactionIn(BaseModel):
    from_id: int
    to_id: int
    amount: confloat(gt=0.0)
    comment: Optional[str] = Field(None, min_length=1, max_length=64)

class TransactionOut(TransactionIn):
    id: int
    created_at: datetime


class CommissionPayer(str, Enum):
    sender='sender'
    receiver='receiver'
    both='both'

    def __str__(self) -> str:
        return self.value
