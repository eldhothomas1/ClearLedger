import { useState, type FormEvent } from "react";
import { createTransaction } from "../api";
import type { TransactionInput } from "../types";

type Props = {
  onSaved: (message: string) => void;
  onCancel: () => void;
};

const emptyForm: TransactionInput = {
  date: new Date().toISOString().slice(0, 10),
  merchant: "",
  amount: "",
  category: "",
};

export default function TransactionForm({ onSaved, onCancel }: Props) {
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  function updateField(field: keyof TransactionInput, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setSaving(true);
    setError("");

    try {
      await createTransaction(form);
      setForm(emptyForm);
      onSaved("Transaction added successfully.");
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
          <h2>Add a transaction</h2>
        </div>
        <button className="text-button" type="button" onClick={onCancel}>
          Close
        </button>
      </div>

      <form className="transaction-form" onSubmit={handleSubmit}>
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
            {saving ? "Saving..." : "Save transaction"}
          </button>
        </div>
      </form>
    </section>
  );
}
