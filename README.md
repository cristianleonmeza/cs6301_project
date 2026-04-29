# cs6301_project
# Secure Multi-Database Cloud Processing Project

This project implements a small cloud-style data processing environment that integrates two independent databases with secure access controls.

## Architecture

- **Database 1 (`users.db`)**: Identity and access management (users, password hashes, roles).
- **Database 2 (`inventory.db`)**: Business data (products, orders).
- **API Layer (FastAPI)**:
  - Authenticates users via `/auth/login`.
  - Enforces bearer-token authorization on protected endpoints.
  - Reads and processes data across both databases.
- **Security Controls**:
  - Password hashing (PBKDF2-SHA256 via Passlib).
  - JWT-based authentication and authorization context.
  - Input validation with Pydantic schemas.
  - Health endpoint for monitoring/validation.

## Endpoints

- `GET /health` – service liveness check.
- `POST /auth/login` – get JWT token.
- `GET /products` – list products (auth required).
- `POST /orders` – create order (auth required).
- `GET /reports/spend` – aggregated spending report (auth required).

## Run Locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then login:

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"analyst","password":"analyst123"}'
```

Use the returned token on protected endpoints:

```bash
curl http://127.0.0.1:8000/products -H "Authorization: Bearer <TOKEN>"
```

## Test

```bash
pytest -q
```

## Notes for cloud deployment

For a production cloud deployment, add:

- TLS termination (HTTPS via load balancer or reverse proxy).
- Secret management for JWT key and DB credentials (not hardcoded).
- Managed database services and network ACLs.
- Centralized logging/monitoring and WAF/rate limiting.