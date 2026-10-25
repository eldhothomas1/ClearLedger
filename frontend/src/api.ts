import type {
  ImportResult,
  SpendingSummary,
  Transaction,
  TransactionFilters,
  TransactionInput,
  TransactionList,
  TokenResponse,
  User,
} from "./types";

const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8001";
const tokenKey = "clearledger_access_token";

export function hasAccessToken() {
  return Boolean(localStorage.getItem(tokenKey));
}

export function clearAccessToken() {
  localStorage.removeItem(tokenKey);
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const headers = new Headers(options?.headers);
  const token = localStorage.getItem(tokenKey);
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const response = await fetch(`${API_URL}${path}`, { ...options, headers });

  if (!response.ok) {
    const data = await response.json().catch(() => null);
    const detail = data?.detail;
    const message = typeof detail === "string" ? detail : "Something went wrong";
    throw new Error(message);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

export async function register(email: string, password: string) {
  return request<User>("/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
}

export async function login(email: string, password: string) {
  const form = new URLSearchParams({ username: email, password });
  const result = await request<TokenResponse>("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: form,
  });
  localStorage.setItem(tokenKey, result.access_token);
  return result;
}

export function getCurrentUser() {
  return request<User>("/auth/me");
}

function addDateFilters(params: URLSearchParams, filters: TransactionFilters) {
  if (filters.dateFrom) params.set("date_from", filters.dateFrom);
  if (filters.dateTo) params.set("date_to", filters.dateTo);
}

export function getSummary(filters: TransactionFilters) {
  const params = new URLSearchParams();
  addDateFilters(params, filters);
  return request<SpendingSummary>(`/analytics/summary?${params}`);
}

export function getTransactions(
  filters: TransactionFilters,
  limit: number,
  offset: number,
) {
  const params = new URLSearchParams({
    limit: String(limit),
    offset: String(offset),
  });

  if (filters.merchant) params.set("merchant", filters.merchant);
  if (filters.category) params.set("category", filters.category);
  addDateFilters(params, filters);

  return request<TransactionList>(`/transactions?${params}`);
}

export function createTransaction(transaction: TransactionInput) {
  return request<Transaction>("/transactions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      ...transaction,
      category: transaction.category || null,
    }),
  });
}

export function deleteTransaction(id: number) {
  return request<void>(`/transactions/${id}`, { method: "DELETE" });
}

export function importTransactions(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  return request<ImportResult>("/transactions/import", {
    method: "POST",
    body: formData,
  });
}
