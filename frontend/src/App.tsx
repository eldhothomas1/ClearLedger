import { useEffect, useState } from "react";

type SpendingSummary = {
  transaction_count: number;
  total_amount: string;
  average_amount: string;
};

const API_URL = "http://127.0.0.1:8001";

function formatCurrency(value: string) {
  return Number(value).toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
  });
}

function App() {
  const [summary, setSummary] = useState<SpendingSummary | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadSummary() {
      try {
        const response = await fetch(`${API_URL}/analytics/summary`);

        if (!response.ok) {
          throw new Error("Unable to load spending summary");
        }

        setSummary(await response.json());
      } catch {
        setError("Start the ClearLedger API to view your spending summary.");
      }
    }

    loadSummary();
  }, []);

  return (
    <main className="page">
      <header className="hero">
        <p className="eyebrow">Personal finance analytics</p>
        <h1>ClearLedger</h1>
        <p className="intro">
          Import transactions, review spending, and understand where your money
          goes.
        </p>
      </header>

      <section className="summary" aria-label="Spending summary">
        <article className="summary-card">
          <p>Transactions</p>
          <strong>{summary?.transaction_count ?? "—"}</strong>
        </article>
        <article className="summary-card">
          <p>Total spending</p>
          <strong>{summary ? formatCurrency(summary.total_amount) : "—"}</strong>
        </article>
        <article className="summary-card">
          <p>Average transaction</p>
          <strong>
            {summary ? formatCurrency(summary.average_amount) : "—"}
          </strong>
        </article>
      </section>

      {error && <p className="error-message">{error}</p>}
    </main>
  );
}

export default App;
