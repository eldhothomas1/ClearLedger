from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Transaction, User
from backend.schemas import CategorySummary, MonthlySummary, SpendingSummary
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

    income_amount = case(
        (Transaction.transaction_type == "income", Transaction.amount),
        else_=0,
    )
    expense_amount = case(
        (Transaction.transaction_type == "expense", Transaction.amount),
        else_=0,
    )
    expense_average = case(
        (Transaction.transaction_type == "expense", Transaction.amount),
        else_=None,
    )
    totals = db.execute(
        select(
            func.count(Transaction.id),
            func.coalesce(func.sum(income_amount), 0),
            func.coalesce(func.sum(expense_amount), 0),
            func.coalesce(func.avg(expense_average), 0),
        ).where(*filters)
    ).one()

    category_name = func.coalesce(Transaction.category, "Uncategorized")
    category_rows = db.execute(
        select(
            category_name.label("category"),
            func.count(Transaction.id).label("transaction_count"),
            func.sum(Transaction.amount).label("total_amount"),
        )
        .where(*filters, Transaction.transaction_type == "expense")
        .group_by(category_name)
        .order_by(func.sum(Transaction.amount).desc())
    ).all()

    return SpendingSummary(
        transaction_count=totals[0],
        total_income=as_money(totals[1]),
        total_expenses=as_money(totals[2]),
        net_cash_flow=as_money(totals[1] - totals[2]),
        average_expense=as_money(totals[3]),
        by_category=[
            CategorySummary(
                category=row.category,
                transaction_count=row.transaction_count,
                total_amount=as_money(row.total_amount),
            )
            for row in category_rows
        ],
    )


@router.get("/monthly", response_model=list[MonthlySummary])
def monthly_spending(
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

    rows = db.execute(
        select(Transaction.date, Transaction.amount, Transaction.transaction_type)
        .where(*filters)
        .order_by(Transaction.date)
    ).all()

    months: dict[str, dict[str, int | Decimal]] = {}
    for row in rows:
        month = row.date.strftime("%Y-%m")
        if month not in months:
            months[month] = {
                "transaction_count": 0,
                "income": Decimal("0"),
                "expenses": Decimal("0"),
            }
        months[month]["transaction_count"] += 1
        months[month]["income" if row.transaction_type == "income" else "expenses"] += row.amount

    return [
        MonthlySummary(
            month=month,
            transaction_count=values["transaction_count"],
            income=as_money(values["income"]),
            expenses=as_money(values["expenses"]),
            net_cash_flow=as_money(values["income"] - values["expenses"]),
        )
        for month, values in months.items()
    ]
