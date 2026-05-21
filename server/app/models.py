from typing import Any, Literal

from pydantic import BaseModel, Field


class RunRequest(BaseModel):
    roll_number: str = Field(..., min_length=1, description="Roll number header value")
    include_negative: bool = True


class TestResult(BaseModel):
    id: str
    name: str
    category: str
    expected_status: int
    actual_status: int
    passed: bool
    response_excerpt: str
    request_payload: dict[str, Any] | None = None
    request_headers: dict[str, str] | None = None


class RunSummary(BaseModel):
    total: int
    passed: int
    failed: int
    success_rate: float


class RunResponse(BaseModel):
    status: Literal["completed"]
    summary: RunSummary
    results: list[TestResult]
