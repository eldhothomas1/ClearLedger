# ClearLedger

[![CI](https://github.com/eldhothomas1/ClearLedger/actions/workflows/tests.yml/badge.svg)](https://github.com/eldhothomas1/ClearLedger/actions/workflows/tests.yml)

ClearLedger is a full-stack personal finance application for importing, managing, and analyzing transaction data. It combines a FastAPI and PostgreSQL backend with a React dashboard.

## Current features

- Create, edit, filter, paginate, and delete transactions from the dashboard
- Register, sign in, restore sessions, and log out through the React interface
- Protect financial data with Argon2 password hashing and JWT authentication
- Isolate transactions, imports, and analytics by user account
- Import CSV and Excel statements through a Pandas validation pipeline
- Recognize common bank column names and batch-check duplicate transactions
- Normalize common bank statement merchant names and fill missing categories
- Track and filter income and expenses separately
- View income, expenses, net cash flow, and category breakdowns
- Compare monthly income and expenses
- Set monthly category budgets and track spending progress
- Validate API requests and responses with Pydantic
- Manage the PostgreSQL schema with Alembic migrations
- Run the API and PostgreSQL together with Docker Compose
- Run isolated backend tests and frontend builds through GitHub Actions
- Use a responsive React and TypeScript interface on desktop and mobile

## Tech stack

- React, TypeScript, and Vite
- Python 3.13
- FastAPI and Pydantic
- Pandas and OpenPyXL
- PostgreSQL
- SQLAlchemy 2.0
- Alembic
- Docker and Docker Compose
- pytest
- GitHub Actions

## Project structure

```text
backend/
├── main.py
├── database.py
├── importer.py
├── models.py
├── processing.py
├── schemas.py
├── security.py
└── routers/
    ├── auth.py
    ├── transactions.py
    ├── budgets.py
    └── analytics.py
frontend/
├── src/
│   ├── components/
│   ├── api.ts
│   ├── App.tsx
│   └── types.ts
└── package.json
alembic/
tests/
sample_data/
```

## Local setup

### Backend

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

3. Install the Python dependencies.

   ```powershell
   python -m pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and enter your PostgreSQL password.

   ```powershell
   Copy-Item .env.example .env
   ```

   Generate a JWT secret and save the result as `JWT_SECRET_KEY` in `.env`.

   ```powershell
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

5. Create a PostgreSQL database named `clearledger` and apply the migrations.

   ```powershell
   python -m alembic upgrade head
   ```

6. Start the API.

   ```powershell
   uvicorn backend.main:app --reload --port 8001
   ```

The API documentation is available at [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs).

### Frontend

Open another PowerShell terminal from the project root.

```powershell
cd frontend
npm install
npm run dev
```

Open the dashboard at [http://127.0.0.1:5173](http://127.0.0.1:5173).

## CSV format

CSV and XLSX files can use common bank headings such as `date`, `posted date`, `merchant`, `description`, `amount`, `debit`, and `credit`. The `category` and `transaction_type` columns are optional. Dates use the `YYYY-MM-DD` format.

```csv
date,merchant,amount,category,transaction_type
2026-10-15,Trader Joe's,48.37,Groceries,expense
2026-10-16,Payroll Deposit,1200.00,Income,income
```

Common statement descriptors for Amazon, Chipotle, Spotify, Trader Joe's, Whole Foods, and Uber are normalized during creation and import. A default category is added only when the category field is empty.

## API overview

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Check API availability |
| `POST` | `/auth/register` | Create an account |
| `POST` | `/auth/login` | Sign in and receive an access token |
| `GET` | `/auth/me` | Retrieve the signed-in user |
| `POST` | `/transactions` | Create a transaction |
| `GET` | `/transactions` | List and filter transactions |
| `POST` | `/transactions/import` | Import transactions from CSV or XLSX |
| `GET` | `/transactions/{id}` | Retrieve one transaction |
| `PATCH` | `/transactions/{id}` | Update selected fields |
| `DELETE` | `/transactions/{id}` | Delete a transaction |
| `GET` | `/analytics/summary` | Get cash-flow totals and category breakdowns |
| `GET` | `/analytics/monthly` | Get monthly income and expense totals |
| `GET` | `/budgets` | List monthly budgets with spending progress |
| `PUT` | `/budgets` | Create or update a category budget |
| `DELETE` | `/budgets/{id}` | Delete a budget |

## Tests

Run the backend tests from the project root.

```powershell
python -m pytest
```

Run a production frontend build from the `frontend` directory.

```powershell
npm run build
```

## Docker

Start PostgreSQL and the API from the project root:

```powershell
docker compose up --build
```

The API runs at `http://127.0.0.1:8001`. PostgreSQL is exposed on port `5433` so it does not conflict with a PostgreSQL service already using port `5432` on Windows. The frontend continues to run locally with `npm run dev`.

## Roadmap

- Configurable categorization rules
- Recurring payment detection
- Cloud deployment
