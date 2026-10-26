from __future__ import annotations

from datetime import date as Date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TransactionBase(BaseModel):
    date: Date
    merchant: str = Field(min_length=1, max_length=255)
    amount: Decimal = Field(max_digits=12, decimal_places=2)
    category: str | None = Field(default=None, max_length=100)

    @field_validator("merchant")
    @classmethod
    def clean_merchant(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if not cleaned:
            raise ValueError("merchant cannot be blank")
        return cleaned

    @field_validator("category")
    @classmethod
    def clean_category(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = " ".join(value.split())
        return cleaned or None


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    date: Date | None = None
    merchant: str | None = Field(default=None, min_length=1, max_length=255)
    amount: Decimal | None = Field(default=None, max_digits=12, decimal_places=2)
    category: str | None = Field(default=None, max_length=100)

    @field_validator("merchant")
    @classmethod
    def clean_optional_merchant(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = " ".join(value.split())
        if not cleaned:
            raise ValueError("merchant cannot be blank")
        return cleaned

    @field_validator("category")
    @classmethod
    def clean_optional_category(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = " ".join(value.split())
        return cleaned or None

    @model_validator(mode="after")
    def reject_null_required_fields(self):
        for field in {"date", "merchant", "amount"} & self.model_fields_set:
            if getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self


class TransactionResponse(TransactionBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class TransactionListResponse(BaseModel):
    items: list[TransactionResponse]
    total: int
    limit: int
    offset: int


class ImportErrorDetail(BaseModel):
    row: int
    message: str


class ImportResponse(BaseModel):
    imported: int
    skipped_duplicates: int
    errors: list[ImportErrorDetail]


class CategorySummary(BaseModel):
    category: str
    transaction_count: int
    total_amount: Decimal


class MonthlySummary(BaseModel):
    month: str
    transaction_count: int
    total_amount: Decimal


class SpendingSummary(BaseModel):
    transaction_count: int
    total_amount: Decimal
    average_amount: Decimal
    by_category: list[CategorySummary]
