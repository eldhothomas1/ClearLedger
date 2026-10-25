from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Transaction, User
from backend.schemas import CategorySummary, SpendingSummary
from backend.security import get_current_user


router = APIRouter(prefix="/analytics", tags=["Analytics"])
CENT = Decimal("0.01")


def as_money(value) -> Decimal:
    return Decimal(str(value)).quantize(CENT)


@router.get("/summary", response_model=SpendingSummary)
def spending_summary(
    date_from: date | None = None,
    date_to: date | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = [Transaction.user_id == current_user.id]
    if date_from:
        filters.append(Transaction.date >= date_from)
    if date_to:
        filters.append(Transaction.date <= date_to)

    totals = db.execute(
        select(
            func.count(Transaction.id),
            func.coalesce(func.sum(Transaction.amount), 0),
            func.coalesce(func.avg(Transaction.amount), 0),
        ).where(*filters)
    ).one()

    category_name = func.coalesce(Transaction.category, "Uncategorized")
    category_rows = db.execute(
        select(
            category_name.label("category"),
            func.count(Transaction.id).label("transaction_count"),
            func.sum(Transaction.amount).label("total_amount"),
        )
        .where(*filters)
        .group_by(category_name)
        .order_by(func.sum(Transaction.amount).desc())
    ).all()

    return SpendingSummary(
        transaction_count=totals[0],
        total_amount=as_money(totals[1]),
        average_amount=as_money(totals[2]),
        by_category=[
            CategorySummary(
                category=row.category,
                transaction_count=row.transaction_count,
                total_amount=as_money(row.total_amount),
            )
            for row in category_rows
        ],
    )
