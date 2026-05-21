from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .models import RunRequest, RunResponse, RunSummary
from .test_engine import run_all_tests

app = FastAPI(
    title="Bajaj API Automation Qualifier",
    description="High-coverage API validation service for qualifier-1",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/run-tests", response_model=RunResponse)
async def run_tests(payload: RunRequest) -> RunResponse:
    try:
        results = await run_all_tests(
            roll_number=payload.roll_number,
            include_negative=payload.include_negative,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Test execution failed: {exc}") from exc

    total = len(results)
    passed = sum(1 for row in results if row.passed)
    failed = total - passed
    rate = round((passed / total) * 100 if total else 0, 2)

    return RunResponse(
        status="completed",
        summary=RunSummary(total=total, passed=passed, failed=failed, success_rate=rate),
        results=results,
    )

