import { useState, type FormEvent } from "react";
import { createTransaction, updateTransaction } from "../api";
import type { Transaction, TransactionInput } from "../types";

type Props = {
  onSaved: (message: string) => void;
  onCancel: () => void;
  transaction?: Transaction | null;
};

function initialForm(transaction?: Transaction | null): TransactionInput {
  return transaction
    ? {
        date: transaction.date,
        merchant: transaction.merchant,
        amount: transaction.amount,
        category: transaction.category ?? "",
        transaction_type: transaction.transaction_type,
      }
    : {
        date: new Date().toISOString().slice(0, 10),
        merchant: "",
        amount: "",
        category: "",
        transaction_type: "expense",
      };
}

export default function TransactionForm({ onSaved, onCancel, transaction }: Props) {
  const [form, setForm] = useState(() => initialForm(transaction));
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  function updateField<K extends keyof TransactionInput>(field: K, value: TransactionInput[K]) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    setError("");

    try {
      if (transaction) {
        await updateTransaction(transaction.id, form);
        onSaved("Transaction updated.");
      } else {
        await createTransaction(form);
        setForm(initialForm());
        onSaved("Transaction added successfully.");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to add transaction");
    } finally {
      setSaving(false);
    }
  }

  return (
    <section className="panel form-panel">
      <div className="section-heading">
        <div>
          <p className="eyebrow">New record</p>
          <h2>{transaction ? "Edit transaction" : "Add a transaction"}</h2>
        </div>
        <button className="text-button" type="button" onClick={onCancel}>
          Close
        </button>
      </div>

      <form className="transaction-form" onSubmit={handleSubmit}>
        <label>
          Type
          <select
            value={form.transaction_type}
            onChange={(event) => updateField(
              "transaction_type",
              event.target.value as TransactionInput["transaction_type"],
            )}
          >
            <option value="expense">Expense</option>
            <option value="income">Income</option>
          </select>
        </label>
        <label>
          Date
          <input
            type="date"
            value={form.date}
            onChange={(event) => updateField("date", event.target.value)}
            required
          />
        </label>
        <label>
          Merchant
          <input
            value={form.merchant}
            onChange={(event) => updateField("merchant", event.target.value)}
            placeholder="Trader Joe's"
            required
          />
        </label>
        <label>
          Amount
          <input
            type="number"
            min="0"
            step="0.01"
            value={form.amount}
            onChange={(event) => updateField("amount", event.target.value)}
            placeholder="48.37"
            required
          />
        </label>
        <label>
          Category
          <input
            value={form.category}
            onChange={(event) => updateField("category", event.target.value)}
            placeholder="Groceries"
          />
        </label>
        <div className="form-actions">
          {error && <p className="form-error">{error}</p>}
          <button className="primary-button" disabled={saving}>
            {saving ? "Saving..." : transaction ? "Update transaction" : "Save transaction"}
          </button>
        </div>
      </form>
    </section>
  );
}
