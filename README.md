# ClearLedger

[![Tests](https://github.com/eldhothomas1/ClearLedger/actions/workflows/tests.yml/badge.svg)](https://github.com/eldhothomas1/ClearLedger/actions/workflows/tests.yml)

ClearLedger is a financial data and analytics API that turns transaction records into searchable, validated data and spending summaries. The current milestone focuses on a production-style Python backend backed by PostgreSQL.

## Current features

- Create, read, update, and delete transactions through a REST API
- Filter transactions by category, merchant, and date range
- Paginate transaction results
- Import CSV statements with row-level validation and duplicate detection
- Calculate overall and per-category spending summaries
- Validate request and response data with Pydantic
- Manage the PostgreSQL schema with Alembic migrations
- Run API tests against an isolated in-memory database
- Run the test suite automatically with GitHub Actions

## Tech stack

- Python 3.13
- FastAPI and Pydantic
- PostgreSQL
- SQLAlchemy 2.0
- Alembic
- pytest

## Project structure

```text
backend/
├── main.py                 # FastAPI application and system endpoints
├── database.py             # Database engine and session management
├── models.py               # SQLAlchemy database models
├── schemas.py              # Pydantic validation and response models
└── routers/
    ├── transactions.py     # Transaction CRUD and CSV import endpoints
    └── analytics.py        # Spending analytics endpoints
alembic/                    # Database migrations
tests/                      # Automated API tests
sample_data/                # Example import file
```

## Local setup

1. Clone the repository and enter the project directory.

   ```powershell
   git clone https://github.com/eldhothomas1/ClearLedger.git
   cd ClearLedger
   ```

2. Create and activate a virtual environment.

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Install the dependencies.

   ```powershell
   python -m pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and enter your PostgreSQL password.

   ```powershell
   Copy-Item .env.example .env
   ```

5. Create a PostgreSQL database named `clearledger`, then apply the migration.

   ```powershell
   alembic upgrade head
   ```

   If the `transactions` table was created manually before Alembic was added, mark the initial migration as applied instead:

   ```powershell
   alembic stamp 20261017_01
   alembic upgrade head
   ```

6. Start the API.

   ```powershell
   uvicorn backend.main:app --reload --port 8001
   ```

Open the interactive documentation at [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs).

## API overview

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Check API availability |
| `POST` | `/transactions` | Create a transaction |
| `GET` | `/transactions` | List and filter transactions |
| `POST` | `/transactions/import` | Import transactions from CSV |
| `GET` | `/transactions/{id}` | Retrieve one transaction |
| `PATCH` | `/transactions/{id}` | Update selected fields |
| `DELETE` | `/transactions/{id}` | Delete a transaction |
| `GET` | `/analytics/summary` | Get totals and category breakdowns |

Example transaction:

```json
{
  "date": "2026-10-15",
  "merchant": "Trader Joe's",
  "amount": "48.37",
  "category": "Groceries"
}
```

CSV files must contain `date`, `merchant`, and `amount` columns. `category` is optional. Dates use the `YYYY-MM-DD` format.

## Tests

Run the test suite from the project root:

```powershell
pytest
```

## Roadmap

- Merchant normalization and configurable categorization rules
- Monthly income and expense trends
- Budget tracking
- React and TypeScript dashboard
- User authentication and account-level data isolation
- Containerized local environment and cloud deployment
