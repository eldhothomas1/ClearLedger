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
    <section className="summary-grid" aria-label="Spending summary">
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
        <strong>{summary ? formatCurrency(summary.average_amount) : "—"}</strong>
      </article>
    </section>
  );
}
