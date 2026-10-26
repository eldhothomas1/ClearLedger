export type Transaction = {
  id: number;
  date: string;
  merchant: string;
  amount: string;
  category: string | null;
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
  total_amount: string;
  average_amount: string;
  by_category: CategorySummary[];
};

export type MonthlySummary = {
  month: string;
  transaction_count: number;
  total_amount: string;
};

export type TransactionInput = {
  date: string;
  merchant: string;
  amount: string;
  category: string;
};

export type TransactionFilters = {
  merchant: string;
  category: string;
  dateFrom: string;
  dateTo: string;
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
