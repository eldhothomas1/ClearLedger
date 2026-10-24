# ClearLedger

[![CI](https://github.com/eldhothomas1/ClearLedger/actions/workflows/tests.yml/badge.svg)](https://github.com/eldhothomas1/ClearLedger/actions/workflows/tests.yml)

ClearLedger is a full-stack personal finance application for importing, managing, and analyzing transaction data. It combines a FastAPI and PostgreSQL backend with a React dashboard.

## Current features

- Create, view, filter, paginate, and delete transactions from the dashboard
- Import CSV statements with row-level validation and duplicate detection
- Filter transactions by merchant, category, and date range
- View transaction totals, average spending, and category breakdowns
- Validate API requests and responses with Pydantic
- Manage the PostgreSQL schema with Alembic migrations
- Run isolated backend tests and frontend builds through GitHub Actions
- Use a responsive React and TypeScript interface on desktop and mobile

## Tech stack

- React, TypeScript, and Vite
- Python 3.13
- FastAPI and Pydantic
- PostgreSQL
- SQLAlchemy 2.0
- Alembic
- pytest
- GitHub Actions

## Project structure

```text
backend/
├── main.py
├── database.py
├── models.py
├── schemas.py
└── routers/
    ├── transactions.py
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

CSV files must contain `date`, `merchant`, and `amount` columns. The `category` column is optional. Dates use the `YYYY-MM-DD` format.

```csv
date,merchant,amount,category
2026-10-15,Trader Joe's,48.37,Groceries
2026-10-16,Spotify,11.99,Entertainment
```

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

## Tests

Run the backend tests from the project root.

```powershell
python -m pytest
```

Run a production frontend build from the `frontend` directory.

```powershell
npm run build
```

## Roadmap

- Merchant normalization and configurable categorization rules
- Monthly income and expense trends
- Budget tracking
- User authentication and account-level data isolation
- Containerized local environment and cloud deployment
