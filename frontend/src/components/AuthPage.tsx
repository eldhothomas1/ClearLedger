import { useState, type FormEvent } from "react";
import { clearAccessToken, getCurrentUser, login, register } from "../api";
import type { User } from "../types";

type Props = {
  onAuthenticated: (user: User) => void;
};

export default function AuthPage({ onAuthenticated }: Props) {
  const [creatingAccount, setCreatingAccount] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  function switchMode() {
    setCreatingAccount((current) => !current);
    setPassword("");
    setConfirmPassword("");
    setError("");
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");

    if (creatingAccount && password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setSubmitting(true);

    try {
      if (creatingAccount) await register(email, password);
      await login(email, password);
      const user = await getCurrentUser();
      onAuthenticated(user);
    } catch (err) {
      clearAccessToken();
      setError(err instanceof Error ? err.message : "Unable to continue");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-intro">
        <a className="brand" href="/">ClearLedger</a>
        <div>
          <p className="eyebrow">Personal finance analytics</p>
          <h1>Understand every dollar.</h1>
          <p className="intro">
            Import transaction data, monitor spending, and keep your financial records organized.
          </p>
        </div>
      </section>

      <section className="auth-card">
        <p className="eyebrow">{creatingAccount ? "Get started" : "Welcome back"}</p>
        <h2>{creatingAccount ? "Create your account" : "Sign in to ClearLedger"}</h2>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label>
            Email
            <input
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              placeholder="you@example.com"
              autoComplete="email"
              required
            />
          </label>
          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="At least 8 characters"
              minLength={8}
              autoComplete={creatingAccount ? "new-password" : "current-password"}
              required
            />
          </label>
          {creatingAccount && (
            <label>
              Confirm password
              <input
                type="password"
                value={confirmPassword}
                onChange={(event) => setConfirmPassword(event.target.value)}
                placeholder="Enter your password again"
                minLength={8}
                autoComplete="new-password"
                required
              />
            </label>
          )}

          {error && <p className="form-error">{error}</p>}

          <button className="primary-button auth-submit" disabled={submitting}>
            {submitting
              ? "Please wait..."
              : creatingAccount
                ? "Create account"
                : "Sign in"}
          </button>
        </form>

        <p className="auth-switch">
          {creatingAccount ? "Already have an account?" : "New to ClearLedger?"}
          <button type="button" onClick={switchMode}>
            {creatingAccount ? "Sign in" : "Create an account"}
          </button>
        </p>
      </section>
    </main>
  );
}
