from datetime import date, datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Budget, Transaction, User
from backend.schemas import BudgetInput, BudgetResponse
from backend.security import get_current_user


router = APIRouter(prefix="/budgets", tags=["Budgets"])
CENT = Decimal("0.01")


def month_start(value: str) -> date:
    return datetime.strptime(value, "%Y-%m").date().replace(day=1)


def next_month(value: date) -> date:
    if value.month == 12:
        return date(value.year + 1, 1, 1)
    return date(value.year, value.month + 1, 1)


def money(value) -> Decimal:
    return Decimal(str(value)).quantize(CENT)


def budget_responses(db: Session, budgets: list[Budget], user_id: int) -> list[BudgetResponse]:
    if not budgets:
        return []

    months = {budget.month for budget in budgets}
    categories = {budget.category.lower() for budget in budgets}
    first_month = min(months)
    final_month = next_month(max(months))
    rows = db.execute(
        select(
            Transaction.date,
            func.lower(Transaction.category).label("category"),
            Transaction.amount,
        ).where(
            Transaction.user_id == user_id,
            Transaction.date >= first_month,
            Transaction.date < final_month,
            Transaction.category.is_not(None),
            func.lower(Transaction.category).in_(categories),
        )
    ).all()

    totals: dict[tuple[date, str], Decimal] = {}
    for row in rows:
        key = (row.date.replace(day=1), row.category)
        totals[key] = totals.get(key, Decimal("0")) + row.amount

    responses = []
    for budget in budgets:
        spent = money(totals.get((budget.month, budget.category.lower()), 0))
        amount = money(budget.amount)
        responses.append(
            BudgetResponse(
                id=budget.id,
                month=budget.month.strftime("%Y-%m"),
                category=budget.category,
                amount=amount,
                spent=spent,
                remaining=money(amount - spent),
                percent_used=money(spent / amount * 100),
            )
        )
    return responses


@router.get("", response_model=list[BudgetResponse])
def list_budgets(
    month: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    statement = select(Budget).where(Budget.user_id == current_user.id)
    if month:
        try:
            selected_month = month_start(month)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail="Month must use YYYY-MM format") from exc
        statement = statement.where(Budget.month == selected_month)

    budgets = db.scalars(
        statement.order_by(Budget.month.desc(), Budget.category)
    ).all()
    return budget_responses(db, list(budgets), current_user.id)


@router.put("", response_model=BudgetResponse)
def save_budget(
    budget_data: BudgetInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    selected_month = month_start(budget_data.month)
    budget = db.scalar(
        select(Budget).where(
            Budget.user_id == current_user.id,
            Budget.month == selected_month,
            func.lower(Budget.category) == budget_data.category.lower(),
        )
    )
    if budget:
        budget.amount = budget_data.amount
        budget.category = budget_data.category
    else:
        budget = Budget(
            user_id=current_user.id,
            month=selected_month,
            category=budget_data.category,
            amount=budget_data.amount,
        )
        db.add(budget)

    db.commit()
    db.refresh(budget)
    return budget_responses(db, [budget], current_user.id)[0]


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    budget = db.scalar(
        select(Budget).where(
            Budget.id == budget_id,
            Budget.user_id == current_user.id,
        )
    )
    if budget is None:
        raise HTTPException(status_code=404, detail="Budget not found")

    db.delete(budget)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
