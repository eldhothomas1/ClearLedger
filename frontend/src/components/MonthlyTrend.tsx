import type { MonthlySummary } from "../types";
import { formatCurrency } from "./SummaryCards";

type Props = {
  months: MonthlySummary[];
};

function formatMonth(month: string) {
  const [year, monthNumber] = month.split("-").map(Number);
  return new Date(year, monthNumber - 1).toLocaleDateString("en-US", {
    month: "short",
    year: "numeric",
  });
}

export default function MonthlyTrend({ months }: Props) {
  const largestAmount = Math.max(...months.map((item) => Number(item.total_amount)), 0);

  return (
    <section className="panel trend-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Trend</p>
          <h2>Monthly spending</h2>
        </div>
        <span>{months.length} months</span>
      </div>

      {months.length === 0 ? (
        <p className="empty-message">Monthly totals will appear here.</p>
      ) : (
        <div className="trend-list">
          {months.map((item) => {
            const width = largestAmount ? (Number(item.total_amount) / largestAmount) * 100 : 0;
            return (
              <div className="trend-row" key={item.month}>
                <span>{formatMonth(item.month)}</span>
                <div className="trend-track">
                  <span style={{ width: `${width}%` }} />
                </div>
                <strong>{formatCurrency(item.total_amount)}</strong>
                <small>{item.transaction_count} transactions</small>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
