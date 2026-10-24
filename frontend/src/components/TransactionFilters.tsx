import { useState, type FormEvent } from "react";
import type { TransactionFilters as FilterValues } from "../types";

type Props = {
  filters: FilterValues;
  onApply: (filters: FilterValues) => void;
};

const emptyFilters: FilterValues = {
  merchant: "",
  category: "",
  dateFrom: "",
  dateTo: "",
};

export default function TransactionFilters({ filters, onApply }: Props) {
  const [form, setForm] = useState(filters);

  function updateField(field: keyof FilterValues, value: string) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  function applyFilters(event: FormEvent) {
    event.preventDefault();
    onApply(form);
  }

  function clearFilters() {
    setForm(emptyFilters);
    onApply(emptyFilters);
  }

  return (
    <form className="filter-bar" onSubmit={applyFilters}>
      <label>
        Merchant
        <input
          value={form.merchant}
          onChange={(event) => updateField("merchant", event.target.value)}
          placeholder="Search merchant"
        />
      </label>
      <label>
        Category
        <input
          value={form.category}
          onChange={(event) => updateField("category", event.target.value)}
          placeholder="e.g. Groceries"
        />
      </label>
      <label>
        From
        <input
          type="date"
          value={form.dateFrom}
          onChange={(event) => updateField("dateFrom", event.target.value)}
        />
      </label>
      <label>
        To
        <input
          type="date"
          value={form.dateTo}
          onChange={(event) => updateField("dateTo", event.target.value)}
        />
      </label>
      <div className="filter-actions">
        <button className="primary-button" type="submit">Apply</button>
        <button className="text-button" type="button" onClick={clearFilters}>Clear</button>
      </div>
    </form>
  );
}
