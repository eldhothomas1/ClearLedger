import io
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pandas as pd


COLUMN_ALIASES = {
    "date": {"date", "transaction date", "posted date", "posting date"},
    "merchant": {"merchant", "description", "details", "payee", "name"},
    "amount": {"amount", "transaction amount"},
    "debit": {"debit", "withdrawal", "charge"},
    "credit": {"credit", "deposit"},
    "category": {"category", "transaction category"},
    "transaction_type": {"type", "transaction type", "credit debit"},
}


def normalized_header(value: object) -> str:
    return re.sub(r"\s+", " ", str(value).strip().lower().replace("_", " "))


def rename_columns(frame: pd.DataFrame) -> pd.DataFrame:
    aliases = {
        alias: target
        for target, names in COLUMN_ALIASES.items()
        for alias in names
    }
    renamed = {}
    claimed = set()
    for column in frame.columns:
        target = aliases.get(normalized_header(column))
        if target and target not in claimed:
            renamed[column] = target
            claimed.add(target)
    return frame.rename(columns=renamed)


def blank(value: object) -> bool:
    return value is None or pd.isna(value) or str(value).strip() == ""


def parse_amount(value: object) -> tuple[Decimal, bool]:
    if blank(value):
        raise ValueError("amount is missing")
    text = str(value).strip()
    negative = text.startswith("-") or (text.startswith("(") and text.endswith(")"))
    cleaned = re.sub(r"[$,()]", "", text).lstrip("+-")
    try:
        return abs(Decimal(cleaned)), negative
    except InvalidOperation as exc:
        raise ValueError("amount is not a valid number") from exc


def normalize_type(value: object, fallback: str) -> str:
    if blank(value):
        return fallback
    normalized = str(value).strip().lower()
    if normalized in {"income", "credit", "deposit"}:
        return "income"
    if normalized in {"expense", "debit", "purchase", "withdrawal"}:
        return "expense"
    raise ValueError("transaction type must be income or expense")


def row_values(row: dict) -> dict:
    debit = row.get("debit")
    credit = row.get("credit")
    type_value = row.get("transaction_type")

    if not blank(debit):
        amount, _ = parse_amount(debit)
        transaction_type = "expense"
    elif not blank(credit):
        amount, _ = parse_amount(credit)
        transaction_type = "income"
    else:
        amount, _ = parse_amount(row.get("amount"))
        transaction_type = normalize_type(type_value, "expense")

    date_value = row.get("date")
    if hasattr(date_value, "strftime"):
        date_value = date_value.strftime("%Y-%m-%d")

    return {
        "date": date_value,
        "merchant": row.get("merchant"),
        "amount": amount,
        "category": None if blank(row.get("category")) else row.get("category"),
        "transaction_type": transaction_type,
    }


def load_statement(filename: str, contents: bytes) -> list[dict]:
    extension = Path(filename).suffix.lower()
    try:
        if extension == ".csv":
            frame = pd.read_csv(io.BytesIO(contents), dtype=object, encoding="utf-8-sig")
        elif extension == ".xlsx":
            frame = pd.read_excel(io.BytesIO(contents), dtype=object)
        else:
            raise ValueError("Only CSV and XLSX files are supported")
    except (UnicodeDecodeError, pd.errors.ParserError, ValueError) as exc:
        if str(exc) == "Only CSV and XLSX files are supported":
            raise
        raise ValueError("The statement file could not be read") from exc

    frame = rename_columns(frame)
    missing = [name for name in ("date", "merchant") if name not in frame.columns]
    has_amount = "amount" in frame.columns or {"debit", "credit"} & set(frame.columns)
    if not has_amount:
        missing.append("amount")
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    return frame.to_dict(orient="records")
