import csv
import io
from datetime import date

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile, status
from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Transaction
from backend.schemas import (
    ImportErrorDetail,
    ImportResponse,
    TransactionCreate,
    TransactionListResponse,
    TransactionResponse,
    TransactionUpdate,
)


router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction_data: TransactionCreate,
    db: Session = Depends(get_db),
):
    transaction = Transaction(**transaction_data.model_dump())
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


@router.get("", response_model=TransactionListResponse)
def list_transactions(
    category: str | None = None,
    merchant: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    filters = []
    if category:
        filters.append(func.lower(Transaction.category) == category.lower())
    if merchant:
        filters.append(Transaction.merchant.ilike(f"%{merchant}%"))
    if date_from:
        filters.append(Transaction.date >= date_from)
    if date_to:
        filters.append(Transaction.date <= date_to)

    total = db.scalar(select(func.count(Transaction.id)).where(*filters)) or 0
    statement = (
        select(Transaction)
        .where(*filters)
        .order_by(Transaction.date.desc(), Transaction.id.desc())
        .limit(limit)
        .offset(offset)
    )
    items = db.scalars(statement).all()
    return TransactionListResponse(items=items, total=total, limit=limit, offset=offset)


@router.post("/import", response_model=ImportResponse)
async def import_transactions(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")

    try:
        contents = (await file.read()).decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="CSV must use UTF-8 encoding") from exc

    reader = csv.DictReader(io.StringIO(contents))
    required_columns = {"date", "merchant", "amount"}
    if not reader.fieldnames or not required_columns.issubset(reader.fieldnames):
        missing = sorted(required_columns - set(reader.fieldnames or []))
        raise HTTPException(
            status_code=400,
            detail=f"Missing required columns: {', '.join(missing)}",
        )

    imported = 0
    skipped_duplicates = 0
    errors: list[ImportErrorDetail] = []
    seen_in_file: set[tuple] = set()

    for row_number, row in enumerate(reader, start=2):
        try:
            data = TransactionCreate.model_validate(
                {
                    "date": row.get("date"),
                    "merchant": row.get("merchant"),
                    "amount": row.get("amount"),
                    "category": row.get("category") or None,
                }
            )
        except ValidationError as exc:
            first_error = exc.errors()[0]
            errors.append(ImportErrorDetail(row=row_number, message=first_error["msg"]))
            continue

        duplicate_key = (data.date, data.merchant.lower(), data.amount)
        exists_in_database = db.scalar(
            select(Transaction.id).where(
                Transaction.date == data.date,
                func.lower(Transaction.merchant) == data.merchant.lower(),
                Transaction.amount == data.amount,
            )
        )
        if duplicate_key in seen_in_file or exists_in_database:
            skipped_duplicates += 1
            continue

        seen_in_file.add(duplicate_key)
        db.add(Transaction(**data.model_dump()))
        imported += 1

    db.commit()
    return ImportResponse(
        imported=imported,
        skipped_duplicates=skipped_duplicates,
        errors=errors,
    )


def get_transaction_or_404(transaction_id: int, db: Session) -> Transaction:
    transaction = db.get(Transaction, transaction_id)
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    return get_transaction_or_404(transaction_id, db)


@router.patch("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction_data: TransactionUpdate,
    db: Session = Depends(get_db),
):
    updates = transaction_data.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="Provide at least one field to update")

    transaction = get_transaction_or_404(transaction_id, db)
    for field, value in updates.items():
        setattr(transaction, field, value)

    db.commit()
    db.refresh(transaction)
    return transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = get_transaction_or_404(transaction_id, db)
    db.delete(transaction)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
