function App() {
  return (
    <main className="page">
      <header className="hero">
        <p className="eyebrow">Personal finance analytics</p>
        <h1>ClearLedger</h1>
        <p className="intro">
          Import transactions, review spending, and understand where your money
          goes.
        </p>
      </header>

      <section className="status-card">
        <div>
          <p className="label">Frontend status</p>
          <h2>Dashboard setup complete</h2>
        </div>
        <span className="status">In progress</span>
        <p>
          The React interface is ready. The next step is connecting it to the
          FastAPI transaction and analytics endpoints.
        </p>
      </section>
    </main>
  );
}

export default App;
