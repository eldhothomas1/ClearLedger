from datetime import date

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile, status
from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.importer import load_statement, row_values
from backend.models import Transaction, User
from backend.processing import normalize_transaction
from backend.schemas import (
    ImportErrorDetail,
    ImportResponse,
    TransactionCreate,
    TransactionListResponse,
    TransactionResponse,
    TransactionUpdate,
)
from backend.security import get_current_user


router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction_data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transaction_values = transaction_data.model_dump()
    merchant, category = normalize_transaction(
        transaction_values["merchant"],
        transaction_values["category"],
    )
    transaction_values["merchant"] = merchant
    transaction_values["category"] = category
    transaction = Transaction(
        **transaction_values,
        user_id=current_user.id,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


@router.get("", response_model=TransactionListResponse)
def list_transactions(
    category: str | None = None,
    merchant: str | None = None,
    transaction_type: str | None = Query(default=None, pattern="^(expense|income)$"),
    date_from: date | None = None,
    date_to: date | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = [Transaction.user_id == current_user.id]
    if category:
        filters.append(func.lower(Transaction.category) == category.lower())
    if merchant:
        filters.append(Transaction.merchant.ilike(f"%{merchant}%"))
    if transaction_type:
        filters.append(Transaction.transaction_type == transaction_type)
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
    current_user: User = Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="File name is required")
    try:
        rows = load_statement(file.filename, await file.read())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    imported = 0
    skipped_duplicates = 0
    errors: list[ImportErrorDetail] = []
    seen_in_file: set[tuple] = set()
    validated: list[tuple[tuple, TransactionCreate]] = []

    for row_number, row in enumerate(rows, start=2):
        try:
            row = row_values(row)
            data = TransactionCreate.model_validate(
                {
                    **row,
                }
            )
        except ValidationError as exc:
            first_error = exc.errors()[0]
            errors.append(ImportErrorDetail(row=row_number, message=first_error["msg"]))
            continue
        except ValueError as exc:
            errors.append(ImportErrorDetail(row=row_number, message=str(exc)))
            continue

        merchant, category = normalize_transaction(data.merchant, data.category)
        data.merchant = merchant
        data.category = category

        duplicate_key = (
            data.date,
            data.merchant.lower(),
            data.amount,
            data.transaction_type,
        )
        if duplicate_key in seen_in_file:
            skipped_duplicates += 1
            continue

        seen_in_file.add(duplicate_key)
        validated.append((duplicate_key, data))

    existing_keys: set[tuple] = set()
    if validated:
        dates = [data.date for _, data in validated]
        existing_rows = db.execute(
            select(
                Transaction.date,
                func.lower(Transaction.merchant),
                Transaction.amount,
                Transaction.transaction_type,
            ).where(
                Transaction.user_id == current_user.id,
                Transaction.date >= min(dates),
                Transaction.date <= max(dates),
            )
        ).all()
        existing_keys = set(existing_rows)

    for duplicate_key, data in validated:
        if duplicate_key in existing_keys:
            skipped_duplicates += 1
            continue
        db.add(Transaction(**data.model_dump(), user_id=current_user.id))
        imported += 1

    db.commit()
    return ImportResponse(
        imported=imported,
        skipped_duplicates=skipped_duplicates,
        errors=errors,
    )


def get_transaction_or_404(
    transaction_id: int,
    user_id: int,
    db: Session,
) -> Transaction:
    transaction = db.scalar(
        select(Transaction).where(
            Transaction.id == transaction_id,
            Transaction.user_id == user_id,
        )
    )
    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_transaction_or_404(transaction_id, current_user.id, db)


@router.patch("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction_data: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    updates = transaction_data.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="Provide at least one field to update")

    transaction = get_transaction_or_404(transaction_id, current_user.id, db)
    if "merchant" in updates:
        merchant, category = normalize_transaction(
            updates["merchant"],
            updates.get("category", transaction.category),
        )
        updates["merchant"] = merchant
        if "category" not in updates and transaction.category is None:
            updates["category"] = category

    for field, value in updates.items():
        setattr(transaction, field, value)

    db.commit()
    db.refresh(transaction)
    return transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transaction = get_transaction_or_404(transaction_id, current_user.id, db)
    db.delete(transaction)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
