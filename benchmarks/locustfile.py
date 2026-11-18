"""Authenticated read-only workload for the ClearLedger FastAPI backend."""
import os
import random
from locust import HttpUser, between, task

class ClearLedgerUser(HttpUser):
    wait_time = between(0.1, 0.4)

    def on_start(self):
        self.headers = {
            "Authorization": f"Bearer {os.environ['BENCHMARK_TOKEN']}"
        }

    @task(5)
    def list_transactions(self):
        params = {"limit": 50, "offset": random.choice([0, 50, 100, 500, 2000, 5000])}
        with self.client.get("/transactions", headers=self.headers, params=params,
                             name="GET /transactions", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"HTTP {response.status_code}: {response.text[:200]}")

    @task(3)
    def summary(self):
        with self.client.get("/analytics/summary", headers=self.headers,
                             name="GET /analytics/summary", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"HTTP {response.status_code}: {response.text[:200]}")

    @task(2)
    def monthly(self):
        with self.client.get("/analytics/monthly", headers=self.headers,
                             name="GET /analytics/monthly", catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"HTTP {response.status_code}: {response.text[:200]}")
