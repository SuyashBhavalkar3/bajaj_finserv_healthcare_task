# Bajaj Qualifier 1 - Top-Tier Submission Kit

This project provides:
- `server/`: FastAPI backend that executes a high-coverage API test suite.
- `client/`: Next.js frontend dashboard to run tests and present results.

## 1) Backend setup (FastAPI + venv)

```powershell
cd "c:\VIT\Placements\Internship\Bajaj\Bajaj Task"
.venv\Scripts\Activate.ps1
pip install -r server\requirements.txt
uvicorn server.app.main:app --reload --port 8000
```

Backend URL: `http://127.0.0.1:8000`

Optional (strict SSL verification):

```powershell
$env:TARGET_API_VERIFY_SSL="true"
```

By default this project keeps SSL verification off for the qualifier endpoint to avoid local certificate-chain issues on restricted networks.

## 2) Frontend setup (Next.js)

```powershell
cd "c:\VIT\Placements\Internship\Bajaj\Bajaj Task\client"
copy .env.local.example .env.local
npm install
npm run dev
```

Frontend URL: `http://127.0.0.1:3000`

## 3) What this validates

Current suite includes 30 test cases across:
- Positive creation
- Missing/empty roll number and header variants
- Duplicate phone
- Duplicate email
- Duplicate phone+email together
- Missing required fields
- Invalid email/phone/field types
- Null values
- Empty/no body
- Extra field behavior
- Whitespace/blank/long text/special char edge cases
- Boundary values (negative/short/float phone etc.)

## 4) API endpoint exposed by backend

`POST /run-tests`

Example body:

```json
{
  "roll_number": "YOUR_ROLL",
  "include_negative": true
}
```
