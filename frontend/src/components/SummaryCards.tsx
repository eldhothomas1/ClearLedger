import type { SpendingSummary } from "../types";

type Props = {
  summary: SpendingSummary | null;
};

export function formatCurrency(value: string | number) {
  return Number(value).toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
  });
}

export default function SummaryCards({ summary }: Props) {
  return (
    <section className="summary-grid" aria-label="Cash flow summary">
      <article className="summary-card">
        <p>Income</p>
        <strong className="income-value">{summary ? formatCurrency(summary.total_income) : "—"}</strong>
      </article>
      <article className="summary-card">
        <p>Expenses</p>
        <strong>{summary ? formatCurrency(summary.total_expenses) : "—"}</strong>
      </article>
      <article className="summary-card">
        <p>Net cash flow</p>
        <strong>{summary ? formatCurrency(summary.net_cash_flow) : "—"}</strong>
      </article>
      <article className="summary-card">
        <p>Transactions</p>
        <strong>{summary?.transaction_count ?? "—"}</strong>
      </article>
    </section>
  );
}
