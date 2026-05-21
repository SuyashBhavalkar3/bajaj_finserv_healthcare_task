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
  const [exporting, setExporting] = useState<"" | "excel" | "pdf">("");

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

  async function downloadExcel() {
    if (!data) return;
    setExporting("excel");
    try {
      const XLSX = await import("xlsx");
      const rows = data.results.map((row) => ({
        ID: row.id,
        "Test Case": row.name,
        Category: row.category,
        Expected: row.expected_status,
        Actual: row.actual_status,
        Status: row.passed ? "PASS" : "FAIL",
        Response: row.response_excerpt,
      }));
      const sheet = XLSX.utils.json_to_sheet(rows);
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, sheet, "TestResults");
      XLSX.writeFile(wb, `bajaj-test-report-${Date.now()}.xlsx`);
    } finally {
      setExporting("");
    }
  }

  async function downloadPdf() {
    if (!data) return;
    setExporting("pdf");
    try {
      const jsPDFModule = await import("jspdf");
      const autoTableModule = await import("jspdf-autotable");
      const jsPDF = jsPDFModule.default;
      const autoTable = autoTableModule.default;
      const doc = new jsPDF({ orientation: "landscape" });
      doc.setFontSize(14);
      doc.text("Bajaj Finserv Health - API Automation Report", 14, 14);
      doc.setFontSize(10);
      doc.text(
        `Run: ${runAt || new Date().toLocaleString()} | Total: ${data.summary.total} | Passed: ${data.summary.passed} | Failed: ${data.summary.failed} | Success: ${data.summary.success_rate}%`,
        14,
        21
      );
      autoTable(doc, {
        startY: 27,
        head: [["ID", "Test Case", "Category", "Expected", "Actual", "Status", "Response"]],
        body: data.results.map((row) => [
          row.id,
          row.name,
          row.category,
          String(row.expected_status),
          String(row.actual_status),
          row.passed ? "PASS" : "FAIL",
          row.response_excerpt,
        ]),
        styles: { fontSize: 8 },
        headStyles: { fillColor: [0, 96, 209] },
        columnStyles: {
          1: { cellWidth: 45 },
          2: { cellWidth: 30 },
          6: { cellWidth: 95 },
        },
      });
      doc.save(`bajaj-test-report-${Date.now()}.pdf`);
    } finally {
      setExporting("");
    }
  }

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
          <div className="actionRow">
            <button
              type="button"
              className="secondaryBtn"
              onClick={downloadExcel}
              disabled={exporting !== ""}
            >
              {exporting === "excel" ? "Preparing Excel..." : "Download Excel"}
            </button>
            <button
              type="button"
              className="secondaryBtn"
              onClick={downloadPdf}
              disabled={exporting !== ""}
            >
              {exporting === "pdf" ? "Preparing PDF..." : "Download PDF"}
            </button>
          </div>
          <ResultTable rows={data.results} />
        </section>
      )}

      {!data && !error && (
        <section className="card emptyState">
          <div className="emptyIcon">BH</div>
          <h3>Ready To Execute Full API Suite</h3>
          <p>
            Enter your roll number and run the suite to view categorized test evidence, then
            export complete results in Excel or PDF for submission.
          </p>
        </section>
      )}
    </main>
  );
}
