from __future__ import annotations

import random
import time
from dataclasses import dataclass
import os
from typing import Any

import httpx

from .models import TestResult

API_URL = "https://createtestuser.in/automation-campus/disabled/create/user"
VERIFY_SSL = os.getenv("TARGET_API_VERIFY_SSL", "false").strip().lower() == "true"


@dataclass
class ApiTestCase:
    id: str
    name: str
    category: str
    expected_status: int
    headers: dict[str, str]
    payload: dict[str, Any] | None


def _new_user(seed: str) -> dict[str, Any]:
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    idx = int(seed[-1]) if seed and seed[-1].isdigit() else 0
    first = f"{letters[idx % 26]}{letters[(idx + 3) % 26]}{letters[(idx + 7) % 26]}"
    last = f"{letters[(idx + 11) % 26]}{letters[(idx + 15) % 26]}{letters[(idx + 19) % 26]}"
    return {
        "firstName": first,
        "lastName": last,
        "phoneNumber": int(f"9{seed[-9:]}"),
        "emailId": f"bajaj.{seed}@example.com",
    }


def _clip(text: str, size: int = 240) -> str:
    if len(text) <= size:
        return text
    return text[: size - 3] + "..."


async def run_all_tests(roll_number: str, include_negative: bool = True) -> list[TestResult]:
    seed_root = str(int(time.time() * 1000)) + str(random.randint(100, 999))
    control_user = _new_user(seed_root)

    default_headers = {
        "Content-Type": "application/json",
        "Cookie": "isUserLoggedIn=true",
        "roll-number": roll_number,
    }

    tests: list[ApiTestCase] = [
        ApiTestCase(
            id="TC01",
            name="Valid user creation",
            category="happy-path",
            expected_status=200,
            headers=default_headers,
            payload=control_user,
        ),
        ApiTestCase(
            id="TC02",
            name="Missing roll-number header",
            category="auth-header",
            expected_status=401,
            headers={k: v for k, v in default_headers.items() if k != "roll-number"},
            payload=_new_user(seed_root + "1"),
        ),
        ApiTestCase(
            id="TC03",
            name="Empty roll-number header",
            category="auth-header",
            expected_status=401,
            headers={**default_headers, "roll-number": ""},
            payload=_new_user(seed_root + "2"),
        ),
    ]

    if include_negative:
        base2 = _new_user(seed_root + "3")
        tests.extend(
            [
                ApiTestCase(
                    id="TC04",
                    name="Duplicate phone number",
                    category="duplicate-checks",
                    expected_status=400,
                    headers=default_headers,
                    payload={**_new_user(seed_root + "4"), "phoneNumber": control_user["phoneNumber"]},
                ),
                ApiTestCase(
                    id="TC05",
                    name="Duplicate email ID",
                    category="duplicate-checks",
                    expected_status=400,
                    headers=default_headers,
                    payload={**_new_user(seed_root + "5"), "emailId": control_user["emailId"]},
                ),
                ApiTestCase(
                    id="TC06",
                    name="Missing firstName",
                    category="required-fields",
                    expected_status=400,
                    headers=default_headers,
                    payload={k: v for k, v in base2.items() if k != "firstName"},
                ),
                ApiTestCase(
                    id="TC07",
                    name="Missing lastName",
                    category="required-fields",
                    expected_status=400,
                    headers=default_headers,
                    payload={k: v for k, v in base2.items() if k != "lastName"},
                ),
                ApiTestCase(
                    id="TC08",
                    name="Missing phoneNumber",
                    category="required-fields",
                    expected_status=400,
                    headers=default_headers,
                    payload={k: v for k, v in base2.items() if k != "phoneNumber"},
                ),
                ApiTestCase(
                    id="TC09",
                    name="Missing emailId",
                    category="required-fields",
                    expected_status=400,
                    headers=default_headers,
                    payload={k: v for k, v in base2.items() if k != "emailId"},
                ),
                ApiTestCase(
                    id="TC10",
                    name="Invalid email format",
                    category="format-validation",
                    expected_status=500,
                    headers=default_headers,
                    payload={**_new_user(seed_root + "6"), "emailId": "bad-email-format"},
                ),
                ApiTestCase(
                    id="TC11",
                    name="Phone number as string",
                    category="type-validation",
                    expected_status=400,
                    headers=default_headers,
                    payload={**_new_user(seed_root + "7"), "phoneNumber": "9000000001"},
                ),
                ApiTestCase(
                    id="TC12",
                    name="Very short phone number",
                    category="boundary-values",
                    expected_status=400,
                    headers=default_headers,
                    payload={**_new_user(seed_root + "8"), "phoneNumber": 12345},
                ),
                ApiTestCase(
                    id="TC13",
                    name="Null emailId",
                    category="required-fields",
                    expected_status=400,
                    headers=default_headers,
                    payload={**_new_user(seed_root + "9"), "emailId": None},
                ),
                ApiTestCase(
                    id="TC14",
                    name="Null phoneNumber",
                    category="required-fields",
                    expected_status=400,
                    headers=default_headers,
                    payload={**_new_user(seed_root + "10"), "phoneNumber": None},
                ),
                ApiTestCase(
                    id="TC15",
                    name="Empty JSON body",
                    category="payload-shape",
                    expected_status=400,
                    headers=default_headers,
                    payload={},
                ),
                ApiTestCase(
                    id="TC16",
                    name="No body",
                    category="payload-shape",
                    expected_status=400,
                    headers=default_headers,
                    payload=None,
                ),
                ApiTestCase(
                    id="TC17",
                    name="Additional unexpected field",
                    category="payload-shape",
                    expected_status=400,
                    headers=default_headers,
                    payload={**_new_user(seed_root + "11"), "unexpected": "extra"},
                ),
                ApiTestCase(
                    id="TC18",
                    name="Whitespace firstName",
                    category="format-validation",
                    expected_status=500,
                    headers=default_headers,
                    payload={**_new_user(seed_root + "12"), "firstName": "   "},
                ),
                ApiTestCase(
                    id="TC19",
                    name="Very long firstName",
                    category="boundary-values",
                    expected_status=500,
                    headers=default_headers,
                    payload={**_new_user(seed_root + "13"), "firstName": "A" * 300},
                ),
                ApiTestCase(
                    id="TC20",
                    name="Special chars in lastName",
                    category="format-validation",
                    expected_status=400,
                    headers=default_headers,
                    payload={**_new_user(seed_root + "14"), "lastName": "O'Connor-#1"},
                ),
                ApiTestCase(
                    id="TC21",
                    name="Duplicate phone and duplicate email together",
                    category="duplicate-checks",
                    expected_status=400,
                    headers=default_headers,
                    payload={
                        **_new_user(seed_root + "15"),
                        "phoneNumber": control_user["phoneNumber"],
                        "emailId": control_user["emailId"],
                    },
                ),
                ApiTestCase(
                    id="TC22",
                    name="Missing Cookie header with valid roll-number",
                    category="auth-header",
                    expected_status=200,
                    headers={k: v for k, v in default_headers.items() if k != "Cookie"},
                    payload=_new_user(seed_root + "16"),
                ),
                ApiTestCase(
                    id="TC23",
                    name="Missing Content-Type header",
                    category="auth-header",
                    expected_status=200,
                    headers={k: v for k, v in default_headers.items() if k != "Content-Type"},
                    payload=_new_user(seed_root + "17"),
                ),
                ApiTestCase(
                    id="TC24",
                    name="Blank emailId string",
                    category="required-fields",
                    expected_status=400,
                    headers=default_headers,
                    payload={**_new_user(seed_root + "18"), "emailId": ""},
                ),
                ApiTestCase(
                    id="TC25",
                    name="Blank lastName string",
                    category="required-fields",
                    expected_status=400,
                    headers=default_headers,
                    payload={**_new_user(seed_root + "19"), "lastName": ""},
                ),
                ApiTestCase(
                    id="TC26",
                    name="firstName numeric",
                    category="type-validation",
                    expected_status=400,
                    headers=default_headers,
                    payload={**_new_user(seed_root + "20"), "firstName": 12345},
                ),
                ApiTestCase(
                    id="TC27",
                    name="lastName as array",
                    category="type-validation",
                    expected_status=400,
                    headers=default_headers,
                    payload={**_new_user(seed_root + "21"), "lastName": ["LAST"]},
                ),
                ApiTestCase(
                    id="TC28",
                    name="phoneNumber as float",
                    category="type-validation",
                    expected_status=400,
                    headers=default_headers,
                    payload={**_new_user(seed_root + "22"), "phoneNumber": 9000000000.12},
                ),
                ApiTestCase(
                    id="TC29",
                    name="phoneNumber as negative integer",
                    category="boundary-values",
                    expected_status=400,
                    headers=default_headers,
                    payload={**_new_user(seed_root + "23"), "phoneNumber": -9000000000},
                ),
                ApiTestCase(
                    id="TC30",
                    name="emailId missing domain",
                    category="format-validation",
                    expected_status=400,
                    headers=default_headers,
                    payload={**_new_user(seed_root + "24"), "emailId": "invalid@"},
                ),
            ]
        )

    results: list[TestResult] = []
    timeout = httpx.Timeout(20.0, connect=10.0)

    async with httpx.AsyncClient(timeout=timeout, verify=VERIFY_SSL) as client:
        for tc in tests:
            response = await client.post(API_URL, headers=tc.headers, json=tc.payload)
            excerpt = _clip(response.text.replace("\n", " "))
            results.append(
                TestResult(
                    id=tc.id,
                    name=tc.name,
                    category=tc.category,
                    expected_status=tc.expected_status,
                    actual_status=response.status_code,
                    passed=response.status_code == tc.expected_status,
                    response_excerpt=excerpt,
                    request_payload=tc.payload,
                    request_headers={k: v for k, v in tc.headers.items() if k.lower() != "cookie"},
                )
            )

    return results
