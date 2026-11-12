export type Transaction = {
  id: number;
  date: string;
  merchant: string;
  amount: string;
  category: string | null;
  transaction_type: "expense" | "income";
};

export type TransactionList = {
  items: Transaction[];
  total: number;
  limit: number;
  offset: number;
};

export type CategorySummary = {
  category: string;
  transaction_count: number;
  total_amount: string;
};

export type SpendingSummary = {
  transaction_count: number;
  total_income: string;
  total_expenses: string;
  net_cash_flow: string;
  average_expense: string;
  by_category: CategorySummary[];
};

export type MonthlySummary = {
  month: string;
  transaction_count: number;
  income: string;
  expenses: string;
  net_cash_flow: string;
};

export type Budget = {
  id: number;
  month: string;
  category: string;
  amount: string;
  spent: string;
  remaining: string;
  percent_used: string;
};

export type BudgetInput = {
  month: string;
  category: string;
  amount: string;
};

export type TransactionInput = {
  date: string;
  merchant: string;
  amount: string;
  category: string;
  transaction_type: "expense" | "income";
};

export type TransactionFilters = {
  merchant: string;
  category: string;
  dateFrom: string;
  dateTo: string;
  transactionType: string;
};

export type ImportResult = {
  imported: number;
  skipped_duplicates: number;
  errors: Array<{ row: number; message: string }>;
};

export type User = {
  id: number;
  email: string;
  created_at: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: string;
};
