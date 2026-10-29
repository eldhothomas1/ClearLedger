import { useState, type FormEvent } from "react";
import type { Budget, BudgetInput } from "../types";
import { formatCurrency } from "./SummaryCards";

type Props = {
  budgets: Budget[];
  month: string;
  onMonthChange: (month: string) => void;
  onSave: (budget: BudgetInput) => Promise<void>;
  onDelete: (budget: Budget) => Promise<void>;
};

export default function BudgetPanel({ budgets, month, onMonthChange, onSave, onDelete }: Props) {
  const [category, setCategory] = useState("");
  const [amount, setAmount] = useState("");
  const [saving, setSaving] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    try {
      await onSave({ month, category, amount });
      setCategory("");
      setAmount("");
    } catch {
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="panel budget-panel" id="budgets">
      <div className="section-heading budget-heading">
        <div>
          <p className="eyebrow">Plan</p>
          <h2>Monthly budgets</h2>
        </div>
        <input
          className="month-input"
          type="month"
          value={month}
          onChange={(event) => onMonthChange(event.target.value)}
        />
      </div>

      <form className="budget-form" onSubmit={submit}>
        <input
          aria-label="Budget category"
          placeholder="Category"
          value={category}
          onChange={(event) => setCategory(event.target.value)}
          required
        />
        <input
          aria-label="Budget amount"
          type="number"
          min="0.01"
          step="0.01"
          placeholder="Monthly limit"
          value={amount}
          onChange={(event) => setAmount(event.target.value)}
          required
        />
        <button className="primary-button" type="submit" disabled={saving}>
          {saving ? "Saving..." : "Save budget"}
        </button>
      </form>

      <div className="budget-list">
        {budgets.length === 0 ? (
          <p className="empty-message">No budgets set for this month.</p>
        ) : (
          budgets.map((budget) => {
            const progress = Math.min(Number(budget.percent_used), 100);
            const overBudget = Number(budget.remaining) < 0;
            return (
              <div className="budget-row" key={budget.id}>
                <div className="budget-summary">
                  <strong>{budget.category}</strong>
                  <span>
                    {formatCurrency(budget.spent)} of {formatCurrency(budget.amount)}
                  </span>
                </div>
                <div className={`budget-track${overBudget ? " over-budget" : ""}`}>
                  <span style={{ width: `${progress}%` }} />
                </div>
                <div className="budget-footer">
                  <small>
                    {overBudget
                      ? `${formatCurrency(Math.abs(Number(budget.remaining)))} over`
                      : `${formatCurrency(budget.remaining)} remaining`}
                  </small>
                  <button className="delete-button" type="button" onClick={() => onDelete(budget)}>
                    Remove
                  </button>
                </div>
              </div>
            );
          })
        )}
      </div>
    </section>
  );
}
