# Bajaj Health Automation Challenge - Qualifier 1 Submission 

FastAPI + Next.js implementation for validating the target create-user API from as many meaningful angles as possible.

## Project structure
- `server/`: FastAPI backend test engine
- `client/`: Next.js dashboard (roll-number input, result table, Excel/PDF export)

## Backend setup (local)
```powershell
cd "c:\VIT\Placements\Internship\Bajaj\Bajaj Task"
.venv\Scripts\Activate.ps1
pip install -r server\requirements.txt
uvicorn server.app.main:app --reload --port 8000
```

Backend URL: `http://127.0.0.1:8000`

Optional strict SSL:
```powershell
$env:TARGET_API_VERIFY_SSL="true"
```

Default behavior keeps SSL verification off to avoid local certificate-chain issues on restricted networks.

## Frontend setup (local)
```powershell
cd "c:\VIT\Placements\Internship\Bajaj\Bajaj Task\client"
copy .env.local.example .env.local
npm install
npm run dev
```

Frontend URL: `http://127.0.0.1:3000`

## Environment configuration
- Local dev: `client/.env.local.example` uses `http://127.0.0.1:8000`
- Production template: `client/.env.production.example` uses Railway backend URL

Set in production host:
- `NEXT_PUBLIC_API_BASE_URL=https://bajajfinservhealthcaretask-production.up.railway.app/`

## Railway backend deployment
Backend-only Docker deploy is supported via:
- `server/Dockerfile`

Build/run locally:
```powershell
cd "c:\VIT\Placements\Internship\Bajaj\Bajaj Task\server"
docker build -t bajaj-backend:local .
docker run -d --name bajaj-backend-local -p 8000:8000 -e PORT=8000 bajaj-backend:local
```

## Test execution API (backend)
`POST /run-tests`

Example request:
```json
{
  "roll_number": "YOUR_ROLL",
  "include_negative": true
}
```

## Coverage summary
Current suite includes **40 hardcoded test cases** across:
- happy path
- missing/empty auth header
- duplicate checks (phone/email/both)
- required field checks
- type validations
- format validations
- payload-shape validations
- boundary-value validations

## Output and evidence
Frontend provides:
- pass/fail summary with success rate
- per-test row with expected vs actual status and response snippet
- export of full run as:
  - Excel (`.xlsx`)
  - PDF (`.pdf`)

## Important note on observed API behavior
The target API can show unstable behavior across some edge cases (for example toggling between `400` and `500` for certain invalid payloads).  
To keep evaluation honest and reproducible, the suite uses strict expected status for stable scenarios and acceptable status sets for known unstable scenarios.

## Submission-ready flow
1. Enter roll number in UI
2. Run full suite
3. Export Excel/PDF report
4. Share summary + report as evidence
