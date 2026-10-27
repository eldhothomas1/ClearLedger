import re


MERCHANT_RULES = (
    (("AMZN", "AMAZON"), "Amazon", "Shopping"),
    (("CHIPOTLE",), "Chipotle", "Dining"),
    (("SPOTIFY",), "Spotify", "Entertainment"),
    (("TRADER JOE",), "Trader Joe's", "Groceries"),
    (("WHOLE FOODS",), "Whole Foods", "Groceries"),
    (("UBER",), "Uber", "Transportation"),
)


def normalize_transaction(merchant: str, category: str | None) -> tuple[str, str | None]:
    cleaned_merchant = re.sub(r"\s+", " ", merchant).strip()
    uppercase_merchant = cleaned_merchant.upper()

    for keywords, name, default_category in MERCHANT_RULES:
        if any(keyword in uppercase_merchant for keyword in keywords):
            return name, category or default_category

    return cleaned_merchant, category
