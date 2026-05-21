"use client";

import { FormEvent, useMemo, useState } from "react";
import ResultTable from "@/components/result-table";
import { RunResponse } from "@/lib/types";

const API_BASE = (process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000").replace(
  /\/$/,
  ""
);

export default function HomePage() {
  const [rollNumber, setRollNumber] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [data, setData] = useState<RunResponse | null>(null);
  const [runAt, setRunAt] = useState("");

  const passRateTone = useMemo(() => {
    const rate = data?.summary.success_rate ?? 0;
    if (rate >= 90) return "pass";
    if (rate >= 70) return "";
    return "fail";
  }, [data]);

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setError("");
    setData(null);
    setRunAt("");
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/run-tests`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ roll_number: rollNumber, include_negative: true }),
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.detail ?? "Test execution failed");
      }
      setData(payload as RunResponse);
      setRunAt(new Date().toLocaleString());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  const submissionSummary = useMemo(() => {
    if (!data) return "";
    return `Bajaj Health Automation Qualifier 1: Executed ${data.summary.total} API test cases using roll-number header validation and multi-angle payload checks. Passed ${data.summary.passed}, failed ${data.summary.failed}, success rate ${data.summary.success_rate}%.`;
  }, [data]);

  return (
    <main className="page">
      <section className="hero">
        <div className="brandRow">
          <span className="brandTag">Bajaj Finserv Health</span>
          <span className="brandSubTag">Qualifier 1 Submission Dashboard</span>
        </div>
        <h1>Bajaj Health API Automation Workbench</h1>
        <p>
          Run high-coverage test scenarios with your roll number and collect clear evidence for
          qualifier evaluation.
        </p>
        <form className="controls" onSubmit={onSubmit}>
          <input
            type="text"
            placeholder="Enter roll number (required)"
            value={rollNumber}
            onChange={(e) => setRollNumber(e.target.value)}
            required
          />
          <button disabled={loading}>{loading ? "Running Tests..." : "Run Full Test Suite"}</button>
        </form>
      </section>

      {error && (
        <section className="card">
          <strong className="fail">Error: </strong>
          <span>{error}</span>
        </section>
      )}

      {data && (
        <section className="card">
          <div className="metaRow">
            <span className="metaLabel">Run Time: {runAt}</span>
          </div>
          <div className="summary">
            <span className="chip">Total: {data.summary.total}</span>
            <span className="chip">Passed: {data.summary.passed}</span>
            <span className="chip">Failed: {data.summary.failed}</span>
            <span className={`chip ${passRateTone}`}>Success: {data.summary.success_rate}%</span>
          </div>
          <div className="submissionBox">
            <h3>Submission Snapshot</h3>
            <p>{submissionSummary}</p>
          </div>
          <ResultTable rows={data.results} />
        </section>
      )}
    </main>
  );
}
