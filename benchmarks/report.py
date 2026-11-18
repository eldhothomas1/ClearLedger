"""Summarize Locust CSV reports without making unsupported performance claims."""
import csv
import json
from pathlib import Path

results = Path("benchmarks/results")
with (results / "locust_stats.csv").open(newline="", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle))
aggregate = next((r for r in rows if r["Name"] == "Aggregated"), None)
if aggregate is None:
    raise RuntimeError("Locust aggregate row not found")
requests = int(aggregate["Request Count"])
failures = int(aggregate["Failure Count"])
p95 = float(aggregate["95%"])
report = {
    "environment": "GitHub Actions ubuntu-latest runner; PostgreSQL 16 service; local HTTP",
    "workload": "60 simulated Locust users; authenticated transaction and analytics GET requests",
    "total_requests": requests,
    "failures": failures,
    "p95_ms": p95,
    "p95_below_200_ms": p95 < 200 and failures == 0,
    "note": "P95 is across read endpoints only; 10k-row import is measured separately. This is a CI-hosted synthetic workload, not production traffic."
}
(results / "summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
markdown = (
    "## ClearLedger benchmark (actual measured result)\n"
    f"- Requests: {requests}; failures: {failures}\n"
    f"- Aggregate P95: **{p95:.1f} ms**\n"
    f"- P95 under 200 ms with no failures: **{report['p95_below_200_ms']}**\n"
    "- Workload: 60 Locust users, read-only authenticated API, PostgreSQL 16, GitHub-hosted runner\n"
    "- Synthetic import of 10,000 rows measured separately\n"
)
(results / "summary.md").write_text(markdown, encoding="utf-8")
print(markdown)
