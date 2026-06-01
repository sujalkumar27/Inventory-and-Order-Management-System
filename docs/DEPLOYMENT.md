# Deployment Guide

A common production layout:

- **Database** → Neon (managed PostgreSQL)
- **Backend** → Render or Railway (Docker / Python service)
- **Frontend** → Vercel or Netlify (static build)

## 1. Database — Neon

1. Create a project at https://neon.tech and a database.
2. Copy the connection string and convert it to the psycopg v3 form:
   `postgresql+psycopg://USER:PASSWORD@HOST/DB?sslmode=require`

## 2. Backend — Render

1. New → **Web Service**, connect the repo, root directory `backend`.
2. Environment: **Docker** (uses `backend/Dockerfile`).
3. Start command (overrides default so migrations run first):
   `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Environment variables:

   | Key                           | Value                                   |
   | ----------------------------- | --------------------------------------- |
   | `DATABASE_URL`                | Neon psycopg URL                        |
   | `SECRET_KEY`                  | long random string                      |
   | `ALGORITHM`                   | `HS256`                                 |
   | `ACCESS_TOKEN_EXPIRE_MINUTES` | `30`                                    |
   | `REFRESH_TOKEN_EXPIRE_DAYS`   | `7`                                     |
   | `BACKEND_CORS_ORIGINS`        | `["https://your-frontend.vercel.app"]`  |

5. Deploy. Public URL: `https://your-backend.onrender.com` (docs at `/docs`).

### Railway (alternative)

`railway init` → add a PostgreSQL plugin (or use Neon) → set the same variables →
`railway up`. Railway injects `$PORT` automatically.

## 3. Frontend — Vercel

1. Import the repo, set the **root directory** to `frontend`.
2. Framework preset: **Vite**. Build command `npm run build`, output `dist`.
3. Environment variable:

   | Key            | Value                                       |
   | -------------- | ------------------------------------------- |
   | `VITE_API_URL` | `https://your-backend.onrender.com/api`     |

4. Deploy. Public URL: `https://your-frontend.vercel.app`.

### Netlify (alternative)

Build command `npm run build`, publish directory `frontend/dist`, add a redirect so
client routing works:

```
/*  /index.html  200
```

Set `VITE_API_URL` under Site settings → Environment.

## 4. Production build commands

```bash
# Backend (image)
docker build -t ioms-backend ./backend

# Frontend (static)
cd frontend && npm install && npm run build   # outputs dist/
```

## 5. Post-deploy checklist

- [ ] `alembic upgrade head` ran against the production DB.
- [ ] `SECRET_KEY` is a strong, unique value (never the default).
- [ ] `BACKEND_CORS_ORIGINS` lists the deployed frontend origin.
- [ ] `VITE_API_URL` points at the deployed backend `/api`.
- [ ] Visit `/docs` on the backend and the login page on the frontend.
