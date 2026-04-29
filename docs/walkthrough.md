# Usage Walkthrough: Secure Multi-DB API

This document explains what happens at each stage when running and validating the project.

## 1) Run automated tests

```bash
pytest -q
```

Expected result:

- `2 passed`
- You may still see deprecation warnings from dependencies.

What this validates:

- `GET /health` returns `200`.
- Login flow works and a valid token can access `GET /products`.

---

## 2) Start API locally

In terminal 1:

```bash
uvicorn app.main:app --reload
```

What each startup line means:

- `Uvicorn running on http://127.0.0.1:8000`: API is live.
- `Started reloader process ...`: auto-reload is enabled.
- `Started server process ...`: request-handling worker is running.
- `Application startup complete.`: startup routine ran successfully.

What startup does in this app:

- Creates both databases/tables if missing.
- Seeds initial users:
  - `admin / admin123`
  - `analyst / analyst123`
- Seeds products:
  - Laptop ($1200)
  - Desk ($300)

---

## 3) Health check

In terminal 2:

```bash
curl http://127.0.0.1:8000/health
```

Expected:

```json
{"status":"ok"}
```

Meaning:

- API process is reachable and route handling works.

---

## 4) Login and receive token

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"analyst","password":"analyst123"}'
```

Expected:

- JSON containing `access_token`.

Meaning:

- Credentials are validated against `users.db`.
- JWT token is issued for protected endpoints.

> Note: If token output appears cut off, that is usually terminal wrapping/prompt formatting.

---

## 5) Save token and call protected endpoint

Capture token:

```bash
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"analyst","password":"analyst123"}' \
  | python -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
```

No output is expected from this command; it stores token in `$TOKEN`.

Call protected route:

```bash
curl http://127.0.0.1:8000/products -H "Authorization: Bearer $TOKEN"
```

Expected:

- JSON array with product data.

Meaning:

- Bearer auth is enforced and accepted.
- Read from `inventory.db` works.

---

## 6) Create order (protected write)

```bash
curl -X POST http://127.0.0.1:8000/orders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id":1,"quantity":2}'
```

Expected:

```json
{"message":"order accepted"}
```

Meaning:

- Protected write endpoint is functioning.
- Order row is inserted in `inventory.db`.

---

## 7) Generate spend report (cross-data processing)

```bash
curl http://127.0.0.1:8000/reports/spend \
  -H "Authorization: Bearer $TOKEN"
```

Expected example:

```json
{"totals_by_user":{"2":2400.0}}
```

Why this value makes sense:

- Product `1` price = `1200.0`
- Quantity ordered = `2`
- Total = `2400.0`

Meaning:

- Aggregation/reporting pipeline works.
- Protected cross-record computation is successful.

---

## 8) Negative checks (security behavior)

### A) Missing token

```bash
curl http://127.0.0.1:8000/products
```

Expected:

```json
{"detail":"Missing bearer token"}
```

Meaning:

- Endpoint is protected and rejects unauthenticated requests.

### B) Bad credentials

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"analyst","password":"wrong"}'
```

Expected:

```json
{"detail":"Bad credentials"}
```

Meaning:

- Authentication failure path behaves correctly.

---

## Final validation checklist

- [x] Service health (`/health`)
- [x] Authentication (`/auth/login`)
- [x] Protected read (`/products`)
- [x] Protected write (`/orders`)
- [x] Reporting (`/reports/spend`)
- [x] Negative auth checks (missing token, bad password)

If all of these pass, your end-to-end demo is complete.