"""Seed 10,000 synthetic transactions through the real authenticated import API."""
import csv
import io
import os
import sys
import time
from datetime import date, timedelta
import requests

base = os.getenv("BENCHMARK_BASE_URL", "http://127.0.0.1:8001")
email = "benchmark@example.test"
password = "LocalBenchmarkPassword-2026!"
session = requests.Session()
register = session.post(base + "/auth/register", json={"email": email, "password": password}, timeout=30)
if register.status_code not in (201, 409):
    raise RuntimeError(f"Registration failed: {register.status_code} {register.text}")
login = session.post(base + "/auth/login", data={"username": email, "password": password}, timeout=30)
login.raise_for_status()
token = login.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

buffer = io.StringIO()
writer = csv.writer(buffer)
writer.writerow(["date", "merchant", "amount", "category", "transaction_type"])
merchants = ["Amazon", "Spotify", "Uber", "Trader Joe's", "Whole Foods", "Chipotle", "Vendor"]
for i in range(10_000):
    day = (date(2025, 1, 1) + timedelta(days=i % 365)).isoformat()
    merchant = f"{merchants[i % len(merchants)]} {i:05d}"
    amount = f"{(i % 5000 + 100) / 100:.2f}"
    category = ["Shopping", "Entertainment", "Transportation", "Groceries", "Dining"][i % 5]
    writer.writerow([day, merchant, amount, category, "expense"])
start = time.perf_counter()
result = session.post(base + "/transactions/import",
                      headers=headers,
                      files={"file": ("synthetic_10000.csv", buffer.getvalue().encode("utf-8"), "text/csv")},
                      timeout=180)
elapsed = time.perf_counter() - start
print(f"Import HTTP status: {result.status_code}; elapsed seconds: {elapsed:.3f}", flush=True)
print(result.text[:1500], flush=True)
result.raise_for_status()
payload = result.json()
if payload.get("imported") != 10_000 or payload.get("errors"):
    raise RuntimeError(f"Expected 10,000 imported with no validation errors, got: {payload}")
summary = session.get(base + "/analytics/summary", headers=headers, timeout=30)
summary.raise_for_status()
if summary.json().get("transaction_count") != 10_000:
    raise RuntimeError(f"Expected 10,000 stored rows: {summary.text}")
with open(os.environ.get("GITHUB_ENV", "/tmp/clearledger_env"), "a", encoding="utf-8") as fh:
    fh.write(f"BENCHMARK_TOKEN={token}\n")
print("Seed success: exactly 10,000 rows visible through the analytics endpoint", flush=True)
