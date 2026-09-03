from datetime import date as Date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class TransactionCreate(BaseModel):
    date: Date
    merchant: str
    amount: Decimal
    category: str | None = None


class TransactionResponse(TransactionCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)