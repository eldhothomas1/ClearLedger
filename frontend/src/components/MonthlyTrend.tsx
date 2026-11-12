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
  const largestAmount = Math.max(
    ...months.flatMap((item) => [Number(item.income), Number(item.expenses)]),
    0,
  );

  return (
    <section className="panel trend-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Trend</p>
          <h2>Monthly cash flow</h2>
        </div>
        <span>{months.length} months</span>
      </div>

      {months.length === 0 ? (
        <p className="empty-message">Monthly totals will appear here.</p>
      ) : (
        <div className="trend-list">
          {months.map((item) => {
            const incomeWidth = largestAmount ? (Number(item.income) / largestAmount) * 100 : 0;
            const expenseWidth = largestAmount ? (Number(item.expenses) / largestAmount) * 100 : 0;
            return (
              <div className="trend-row" key={item.month}>
                <span>{formatMonth(item.month)}</span>
                <div className="trend-bars">
                  <div className="trend-track income-track">
                    <span style={{ width: `${incomeWidth}%` }} />
                  </div>
                  <div className="trend-track expense-track">
                    <span style={{ width: `${expenseWidth}%` }} />
                  </div>
                </div>
                <div className="trend-amounts">
                  <span>{formatCurrency(item.income)} in</span>
                  <span>{formatCurrency(item.expenses)} out</span>
                </div>
                <strong className={Number(item.net_cash_flow) >= 0 ? "income-value" : "expense-value"}>
                  {formatCurrency(item.net_cash_flow)}
                </strong>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
