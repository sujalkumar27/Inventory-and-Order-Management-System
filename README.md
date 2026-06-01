# Inventory & Order Management System

A production-ready, full-stack inventory and order management platform.

- **Backend:** Python 3.12 · FastAPI · SQLAlchemy 2 · Alembic · PostgreSQL · JWT
- **Frontend:** React 18 · Vite · React Router · Axios · Tailwind CSS · React Hook Form · Recharts
- **DevOps:** Docker · Docker Compose · GitHub Actions CI/CD

---

## Features

- 🔐 **Auth** — registration, JWT login with **refresh tokens**, protected routes, Admin/User **RBAC**
- 📦 **Products** — CRUD, unique SKU, non-negative price/stock, search, pagination, sort by name/price, filter by stock
- 👥 **Customers** — CRUD, unique email, search, pagination
- 🧾 **Orders** — multi-item orders with automatic **stock validation, deduction, and total calculation**; status workflow (pending → processing → completed / cancelled)
- 📊 **Dashboard** — stat cards + charts (monthly orders, revenue trend, top sellers, low stock)
- 🛡️ Global exception handling with a consistent `{ success, message }` error envelope
- 🎁 **Bonus:** soft delete, audit logs, inventory history tracking, CSV export, dark mode, RBAC

## Architecture

```
┌────────────┐      HTTPS/JSON      ┌────────────┐      SQL      ┌────────────┐
│  Frontend  │  ───────────────▶   │  Backend   │  ─────────▶  │ PostgreSQL │
│  React+Vite│  ◀───────────────   │  FastAPI   │  ◀─────────  │            │
└────────────┘     JWT bearer       └────────────┘               └────────────┘
        nginx :3000                  uvicorn :8000                    :5432
```

Backend layering: `api` (routing) → `services` (business logic) → `models` (ORM) →
`db`. Validation/serialization via Pydantic `schemas`. See
[docs/DATABASE.md](docs/DATABASE.md) for the ER diagram and schema.

```
backend/                          frontend/
├── app/                          ├── src/
│   ├── api/      (routes, deps)   │   ├── api/        (axios client + resources)
│   ├── core/     (config, jwt)    │   ├── components/ (shared UI)
│   ├── db/       (session, base)  │   ├── context/    (auth, theme)
│   ├── models/   (SQLAlchemy)     │   ├── hooks/
│   ├── schemas/  (Pydantic)       │   ├── layouts/
│   ├── services/ (logic)          │   ├── pages/      (auth, dashboard, products…)
│   ├── utils/                     │   ├── routes/     (ProtectedRoute)
│   └── main.py                    │   └── App.jsx
├── alembic/                       ├── Dockerfile
├── tests/                         └── .env.example
├── Dockerfile
└── requirements.txt
```

---

## Quick start (Docker)

```bash
cp .env.example .env          # edit SECRET_KEY etc.
docker compose up --build
```

- Frontend → http://localhost:3000
- Backend API → http://localhost:8000/api
- Swagger UI → http://localhost:8000/docs
- PostgreSQL → localhost:5432

Migrations run automatically on backend startup. If `FIRST_ADMIN_EMAIL` /
`FIRST_ADMIN_PASSWORD` are set, an admin account is created on boot.

## Local development (without Docker)

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                   # point DATABASE_URL at your Postgres
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env                                   # VITE_API_URL=http://localhost:8000/api
npm run dev                                            # http://localhost:5173
```

---

## API endpoints

| Area      | Endpoints                                                              |
| --------- | --------------------------------------------------------------------- |
| Auth      | `POST /api/auth/register` · `POST /api/auth/login` · `POST /api/auth/refresh` · `GET /api/auth/me` |
| Products  | `GET/POST /api/products` · `GET/PUT/DELETE /api/products/{id}`         |
| Customers | `GET/POST /api/customers` · `GET/PUT/DELETE /api/customers/{id}`       |
| Orders    | `GET/POST /api/orders` · `GET/PUT/DELETE /api/orders/{id}`             |
| Dashboard | `GET /api/dashboard/stats` · `GET /api/dashboard/products/export`      |

Full reference: [docs/API.md](docs/API.md) · Postman: [docs/postman_collection.json](docs/postman_collection.json)

## Order business logic

Creating an order validates the customer and products, checks stock for each line,
and **rejects the whole order** if any item is short:

```json
{ "success": false, "message": "Insufficient inventory" }
```

On success it deducts inventory, records inventory history, and computes the total
automatically. Cancelling or deleting an order restores stock.

---

## Testing

```bash
# Backend (needs a Postgres test DB; see TEST_DATABASE_URL)
cd backend && pytest

# Frontend
cd frontend && npm test
```

Coverage includes authentication, product CRUD, customer CRUD, order creation and
inventory validation (see `backend/tests/`).

## CI/CD

[.github/workflows/ci.yml](.github/workflows/ci.yml) runs backend tests (with a
Postgres service), builds + tests the frontend, and builds both Docker images on
every push and PR.

## Deployment

Frontend on Vercel/Netlify, backend on Render/Railway, database on Neon — see
[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for step-by-step instructions, environment
variables, production build commands and public URLs.

## Environment variables

**Backend** — `DATABASE_URL`, `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`,
`REFRESH_TOKEN_EXPIRE_DAYS`, `BACKEND_CORS_ORIGINS`.
**Frontend** — `VITE_API_URL`.

Secrets are never hardcoded; copy `.env.example` → `.env` and fill in values.

## Screenshots

> Run the app and capture these for your submission:
> Login · Dashboard (charts) · Products · Order creation · Order details.

## License

MIT
