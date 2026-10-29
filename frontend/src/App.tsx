import { useCallback, useEffect, useState } from "react";
import {
  clearAccessToken,
  deleteBudget,
  deleteTransaction,
  getBudgets,
  getCurrentUser,
  getMonthlySummary,
  getSummary,
  getTransactions,
  hasAccessToken,
  saveBudget,
} from "./api";
import AuthPage from "./components/AuthPage";
import BudgetPanel from "./components/BudgetPanel";
import CategoryBreakdown from "./components/CategoryBreakdown";
import ImportPanel from "./components/ImportPanel";
import MonthlyTrend from "./components/MonthlyTrend";
import SummaryCards from "./components/SummaryCards";
import TransactionFilters from "./components/TransactionFilters";
import TransactionForm from "./components/TransactionForm";
import TransactionTable from "./components/TransactionTable";
import type {
  Budget,
  BudgetInput,
  SpendingSummary,
  MonthlySummary,
  Transaction,
  TransactionFilters as FilterValues,
  User,
} from "./types";

const pageSize = 10;
const currentMonth = new Date().toISOString().slice(0, 7);
const emptyFilters: FilterValues = {
  merchant: "",
  category: "",
  dateFrom: "",
  dateTo: "",
};

type DashboardProps = {
  user: User;
  onLogout: () => void;
};

function Dashboard({ user, onLogout }: DashboardProps) {
  const [summary, setSummary] = useState<SpendingSummary | null>(null);
  const [monthlySummary, setMonthlySummary] = useState<MonthlySummary[]>([]);
  const [budgets, setBudgets] = useState<Budget[]>([]);
  const [budgetMonth, setBudgetMonth] = useState(currentMonth);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [total, setTotal] = useState(0);
  const [filters, setFilters] = useState(emptyFilters);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [refreshCount, setRefreshCount] = useState(0);

  const loadDashboard = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const [summaryData, monthlyData, budgetData, transactionData] = await Promise.all([
        getSummary(filters),
        getMonthlySummary(filters),
        getBudgets(budgetMonth),
        getTransactions(filters, pageSize, (page - 1) * pageSize),
      ]);
      setSummary(summaryData);
      setMonthlySummary(monthlyData);
      setBudgets(budgetData);
      setTransactions(transactionData.items);
      setTotal(transactionData.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load dashboard");
    } finally {
      setLoading(false);
    }
  }, [filters, page, budgetMonth]);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard, refreshCount]);

  function refreshDashboard(nextMessage: string) {
    setMessage(nextMessage);
    setError("");
    setPage(1);
    setShowForm(false);
    setRefreshCount((count) => count + 1);
  }

  function applyFilters(nextFilters: FilterValues) {
    setFilters(nextFilters);
    setPage(1);
    setMessage("");
  }

  async function removeTransaction(transaction: Transaction) {
    const confirmed = window.confirm(`Delete the ${transaction.merchant} transaction?`);
    if (!confirmed) return;

    try {
      await deleteTransaction(transaction.id);
      refreshDashboard("Transaction deleted.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to delete transaction");
    }
  }

  async function storeBudget(budget: BudgetInput) {
    try {
      await saveBudget(budget);
      refreshDashboard("Budget saved.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to save budget");
      throw err;
    }
  }

  async function removeBudget(budget: Budget) {
    try {
      await deleteBudget(budget.id);
      refreshDashboard("Budget removed.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to remove budget");
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="#top">ClearLedger</a>
        <nav>
          <a href="#budgets">Budgets</a>
          <a href="#transactions">Transactions</a>
          <a href="#import">Import</a>
          <button className="primary-button" type="button" onClick={() => setShowForm(true)}>
            Add transaction
          </button>
          <div className="account-menu">
            <span>{user.email}</span>
            <button className="text-button" type="button" onClick={onLogout}>Log out</button>
          </div>
        </nav>
      </header>

      <main className="page" id="top">
        <section className="hero">
          <div>
            <p className="eyebrow">Financial overview</p>
            <h1>Your spending, made clear.</h1>
            <p className="intro">
              Review transactions, import statement data, and understand where your money goes.
            </p>
          </div>
          <button className="hero-button" type="button" onClick={() => setShowForm(true)}>
            Add transaction
          </button>
        </section>

        {message && <div className="notice success-notice">{message}</div>}
        {error && <div className="notice error-notice">{error}</div>}

        <SummaryCards summary={summary} />

        <BudgetPanel
          budgets={budgets}
          month={budgetMonth}
          onMonthChange={setBudgetMonth}
          onSave={storeBudget}
          onDelete={removeBudget}
        />

        <MonthlyTrend months={monthlySummary} />

        {showForm && (
          <TransactionForm onSaved={refreshDashboard} onCancel={() => setShowForm(false)} />
        )}

        <div className="dashboard-grid">
          <CategoryBreakdown categories={summary?.by_category ?? []} />
          <ImportPanel onImported={refreshDashboard} />
        </div>

        <section id="transactions" className="transactions-section">
          <TransactionFilters filters={filters} onApply={applyFilters} />
          <TransactionTable
            transactions={transactions}
            total={total}
            page={page}
            pageSize={pageSize}
            loading={loading}
            onPageChange={setPage}
            onDelete={removeTransaction}
          />
        </section>
      </main>
    </div>
  );
}

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [checkingSession, setCheckingSession] = useState(true);

  useEffect(() => {
    async function restoreSession() {
      if (!hasAccessToken()) {
        setCheckingSession(false);
        return;
      }

      try {
        setUser(await getCurrentUser());
      } catch {
        clearAccessToken();
      } finally {
        setCheckingSession(false);
      }
    }

    restoreSession();
  }, []);

  function logout() {
    clearAccessToken();
    setUser(null);
  }

  if (checkingSession) {
    return <div className="session-loading">Loading ClearLedger...</div>;
  }

  if (!user) {
    return <AuthPage onAuthenticated={setUser} />;
  }

  return <Dashboard user={user} onLogout={logout} />;
}

export default App;
