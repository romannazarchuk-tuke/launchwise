"""Bad input must give 4xx with a readable JSON message, never 500.

Usage: python3 qa/api_fuzz.py [API_BASE]
Default target is uvicorn directly (http://127.0.0.1:8000/api), so the nginx rate limit
on POST /api/plans doesn't interfere; the API's own validation is what's being tested.
"""

import json
import sys
import urllib.error
import urllib.request

API = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000/api"
VALID = {"business_type": "coffee_shop", "goal": "bookings", "audience": "local", "languages": ["en"],
         "features": [], "budget": "starter", "timeline": "asap"}


def call(method: str, path: str, body=None, raw: bytes | None = None, ctype="application/json"):
    data = raw if raw is not None else (json.dumps(body).encode() if body is not None else None)
    req = urllib.request.Request(API + path, data=data, method=method, headers={"Content-Type": ctype})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


CASES = [
    ("empty body", dict(raw=b"")),
    ("not JSON", dict(raw=b"{business_type:")),
    ("JSON array", dict(body=[1, 2, 3])),
    ("JSON string", dict(body="coffee")),
    ("form encoded", dict(raw=b"business_type=coffee_shop", ctype="application/x-www-form-urlencoded")),
    ("missing everything", dict(body={})),
    ("unknown business", dict(body={**VALID, "business_type": "bakery"})),
    ("wrong case", dict(body={**VALID, "business_type": "Coffee_Shop"})),
    ("number instead of string", dict(body={**VALID, "goal": 3})),
    ("null goal", dict(body={**VALID, "goal": None})),
    ("4 languages", dict(body={**VALID, "languages": ["en", "de", "fr", "es"]})),
    ("no languages", dict(body={**VALID, "languages": []})),
    ("languages not a list", dict(body={**VALID, "languages": "en"})),
    ("duplicate features", dict(body={**VALID, "features": ["blog", "blog"]})),
    ("10 features", dict(body={**VALID, "features": ["blog"] * 10})),
    ("unknown feature", dict(body={**VALID, "features": ["teleport"]})),
    ("nested object", dict(body={**VALID, "features": [{"a": 1}]})),
    ("name 200 chars", dict(body={**VALID, "business_name": "x" * 200})),
    ("name is a number", dict(body={**VALID, "business_name": 42})),
    ("extra field", dict(body={**VALID, "admin": True})),
    ("unicode name ok?", dict(body={**VALID, "business_name": "Café Ünïcødé 🍰"})),
    ("script in name", dict(body={**VALID, "business_name": "<script>alert(1)</script>"})),
]


def main() -> None:
    bad = 0
    for name, kw in CASES:
        status, text = call("POST", "/plans", **kw)
        ok_json = text.startswith("{") and "Traceback" not in text and "detail" in text
        expected = status in (201,) if name in ("unicode name ok?", "script in name") else status == 422
        flag = "OK " if expected and (ok_json or status == 201) else "BAD"
        bad += flag == "BAD"
        print(f"{flag} {status} {name:26} {text[:110]}")
    for method, path in [("GET", "/plans/AAAAAAAAAA"), ("GET", "/plans/" + "a" * 500), ("GET", "/plans/../../etc/passwd"),
                         ("GET", "/plans/abcdefghij/export?format=pdf"), ("GET", "/examples?business_type=1%27%20OR%201=1"),
                         ("DELETE", "/plans/l34kndqa5h"), ("PUT", "/plans/l34kndqa5h")]:
        status, text = call(method, path)
        flag = "OK " if 400 <= status < 500 and "Traceback" not in text else "BAD"
        bad += flag == "BAD"
        print(f"{flag} {status} {method} {path[:40]:40} {text[:80]}")
    print("ALL 4xx, NO 500" if not bad else f"{bad} PROBLEMS")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
