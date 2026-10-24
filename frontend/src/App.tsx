import { useEffect, useState } from "react";

type SpendingSummary = {
  transaction_count: number;
  total_amount: string;
  average_amount: string;
};

type Transaction = {
  id: number;
  date: string;
  merchant: string;
  amount: string;
  category: string | null;
};

type TransactionList = {
  items: Transaction[];
};

const API_URL = "http://127.0.0.1:8001";

function formatCurrency(value: string) {
  return Number(value).toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
  });
}

function formatDate(value: string) {
  return new Date(`${value}T00:00:00`).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function App() {
  const [summary, setSummary] = useState<SpendingSummary | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [summaryResponse, transactionsResponse] = await Promise.all([
          fetch(`${API_URL}/analytics/summary`),
          fetch(`${API_URL}/transactions?limit=5`),
        ]);

        if (!summaryResponse.ok || !transactionsResponse.ok) {
          throw new Error("Unable to load dashboard");
        }

        const summaryData: SpendingSummary = await summaryResponse.json();
        const transactionData: TransactionList =
          await transactionsResponse.json();

        setSummary(summaryData);
        setTransactions(transactionData.items);
      } catch {
        setError("Start the ClearLedger API to view your dashboard.");
      }
    }

    loadDashboard();
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

      <section className="transactions-section">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Activity</p>
            <h2>Recent transactions</h2>
          </div>
          <span>Latest 5</span>
        </div>

        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Merchant</th>
                <th>Category</th>
                <th>Date</th>
                <th className="amount">Amount</th>
              </tr>
            </thead>
            <tbody>
              {transactions.length === 0 ? (
                <tr>
                  <td className="empty-state" colSpan={4}>
                    No transactions to display.
                  </td>
                </tr>
              ) : (
                transactions.map((transaction) => (
                  <tr key={transaction.id}>
                    <td className="merchant">{transaction.merchant}</td>
                    <td>{transaction.category ?? "Uncategorized"}</td>
                    <td>{formatDate(transaction.date)}</td>
                    <td className="amount">
                      {formatCurrency(transaction.amount)}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}

export default App;
