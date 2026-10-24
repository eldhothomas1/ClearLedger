import type { CategorySummary } from "../types";
import { formatCurrency } from "./SummaryCards";

type Props = {
  categories: CategorySummary[];
};

export default function CategoryBreakdown({ categories }: Props) {
  const largestAmount = Math.max(...categories.map((item) => Number(item.total_amount)), 0);

  return (
    <section className="panel category-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Breakdown</p>
          <h2>Spending by category</h2>
        </div>
      </div>

      <div className="category-list">
        {categories.length === 0 ? (
          <p className="empty-message">Category totals will appear here.</p>
        ) : (
          categories.map((item) => {
            const width = largestAmount ? (Number(item.total_amount) / largestAmount) * 100 : 0;
            return (
              <div className="category-row" key={item.category}>
                <div className="category-details">
                  <span>{item.category}</span>
                  <strong>{formatCurrency(item.total_amount)}</strong>
                </div>
                <div className="category-track">
                  <span style={{ width: `${width}%` }} />
                </div>
                <small>{item.transaction_count} transactions</small>
              </div>
            );
          })
        )}
      </div>
    </section>
  );
}
