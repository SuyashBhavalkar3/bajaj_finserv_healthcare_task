"use client";

import { TestResult } from "@/lib/types";

type Props = {
  rows: TestResult[];
};

export default function ResultTable({ rows }: Props) {
  return (
    <div className="tableWrap">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Test Case</th>
            <th>Category</th>
            <th>Expected</th>
            <th>Actual</th>
            <th>Status</th>
            <th>Response</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.id}>
              <td>{row.id}</td>
              <td>{row.name}</td>
              <td>{row.category}</td>
              <td>{row.expected_status}</td>
              <td>{row.actual_status}</td>
              <td>
                <span className={row.passed ? "pill pass" : "pill fail"}>
                  {row.passed ? "PASS" : "FAIL"}
                </span>
              </td>
              <td title={row.response_excerpt}>{row.response_excerpt}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
