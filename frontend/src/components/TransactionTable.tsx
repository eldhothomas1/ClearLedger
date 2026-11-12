import { formatCurrency } from "./SummaryCards";
import type { Transaction } from "../types";

type Props = {
  transactions: Transaction[];
  total: number;
  page: number;
  pageSize: number;
  loading: boolean;
  onPageChange: (page: number) => void;
  onEdit: (transaction: Transaction) => void;
  onDelete: (transaction: Transaction) => void;
};

function formatDate(value: string) {
  return new Date(`${value}T00:00:00`).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export default function TransactionTable({
  transactions,
  total,
  page,
  pageSize,
  loading,
  onPageChange,
  onEdit,
  onDelete,
}: Props) {
  const lastPage = Math.max(1, Math.ceil(total / pageSize));

  return (
    <section className="panel transactions-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Activity</p>
          <h2>Transactions</h2>
        </div>
        <span>{total} total</span>
      </div>

      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Merchant</th>
              <th>Category</th>
              <th>Type</th>
              <th>Date</th>
              <th className="amount">Amount</th>
              <th aria-label="Actions" />
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td className="empty-state" colSpan={6}>Loading transactions...</td>
              </tr>
            ) : transactions.length === 0 ? (
              <tr>
                <td className="empty-state" colSpan={6}>No transactions found.</td>
              </tr>
            ) : (
              transactions.map((transaction) => (
                <tr key={transaction.id}>
                  <td className="merchant">{transaction.merchant}</td>
                  <td><span className="category-tag">{transaction.category ?? "Uncategorized"}</span></td>
                  <td><span className={`type-tag ${transaction.transaction_type}`}>{transaction.transaction_type}</span></td>
                  <td>{formatDate(transaction.date)}</td>
                  <td className={`amount ${transaction.transaction_type}`}>
                    {transaction.transaction_type === "income" ? "+" : "-"}
                    {formatCurrency(transaction.amount)}
                  </td>
                  <td className="action-cell">
                    <button
                      className="text-button"
                      type="button"
                      onClick={() => onEdit(transaction)}
                    >
                      Edit
                    </button>
                    <button
                      className="delete-button"
                      type="button"
                      onClick={() => onDelete(transaction)}
                      aria-label={`Delete ${transaction.merchant} transaction`}
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <div className="pagination">
        <button
          className="secondary-button"
          type="button"
          disabled={page === 1}
          onClick={() => onPageChange(page - 1)}
        >
          Previous
        </button>
        <span>Page {page} of {lastPage}</span>
        <button
          className="secondary-button"
          type="button"
          disabled={page >= lastPage}
          onClick={() => onPageChange(page + 1)}
        >
          Next
        </button>
      </div>
    </section>
  );
}
