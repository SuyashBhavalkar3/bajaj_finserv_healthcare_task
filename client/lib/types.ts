export type TestResult = {
  id: string;
  name: string;
  category: string;
  expected_status: number;
  actual_status: number;
  passed: boolean;
  response_excerpt: string;
  request_payload: Record<string, unknown> | null;
  request_headers: Record<string, string> | null;
};

export type RunResponse = {
  status: "completed";
  summary: {
    total: number;
    passed: number;
    failed: number;
    success_rate: number;
  };
  results: TestResult[];
};
