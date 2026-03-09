# Pitwall

A prediction game for F1 fans — the digital version of a game played with friends for years.

Each race, every player in a game picks who they think will finish 10th and who will DNF first. Points are awarded based on how close your 10th-place pick was, and whether you nailed the DNF. Predictions lock at the official session start time.

**Live:** https://pitwall-tau.vercel.app

---

## How scoring works

Each race scores two predictions:

**10th place** — points scale with how far off your pick was:

| Positions off | Points |
|---|---|
| 0 (exact) | 25 |
| 1 | 18 |
| 2 | 15 |
| 3 | 12 |
| 4 | 10 |
| 5 | 8 |
| 6 | 6 |
| 7 | 4 |
| 8 | 2 |
| 9 | 1 |
| 10+ | 0 |

**First DNF** — 10 points for the correct driver, 0 otherwise.

Maximum per race: 35 points.

---

## Stack

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/) — REST API
- [SQLModel](https://sqlmodel.tiangolo.com/) — ORM (built on SQLAlchemy + Pydantic)
- [PostgreSQL](https://www.postgresql.org/) — database
- [Alembic](https://alembic.sqlalchemy.org/) — schema migrations
- [APScheduler](https://apscheduler.readthedocs.io/) — scheduled email reminders
- [Resend](https://resend.com/) — transactional email
- [uv](https://docs.astral.sh/uv/) — package management

**Frontend**
- [React 18](https://react.dev/) + [TypeScript](https://www.typescriptlang.org/)
- [Vite](https://vitejs.dev/)

**Data**
- [Jolpica F1 API](https://github.com/jolpica/jolpica-f1) — F1 schedule, results, and driver data

---

## Project structure

```
pitwall/
  backend/
    app/
      api/routes/     # FastAPI route handlers
      core/           # Config, security, error types
      crud/           # Database query functions
      db/             # Engine, session, migrations
      models/         # SQLModel table definitions
      schema/         # Enums and non-table schemas
      services/       # Ingestor, scorer, email, F1 client
    alembic/          # Migration scripts
    bruno/            # Bruno API collection
    Dockerfile
  frontend/
    src/
      pages/          # Game, Games, Auth pages
      api.ts          # Typed API client
  .github/workflows/  # GitHub Actions (manual ingest trigger)
```

---

## Auth

Authentication uses JWT bearer tokens (HS256). There are no refresh tokens — the access token is long-lived and stored in `localStorage`.

**Registration:** `POST /user/` with `name`, `email`, `password`

**Login:** `POST /auth/token` (OAuth2 password flow) returns `{ access_token, token_type }`

All protected routes read the token from the `Authorization: Bearer <token>` header. Passwords are hashed with bcrypt.

---

## Games

A game is tied to a specific F1 season. The owner creates it and shares a 6-character invite code. Anyone with an account can join using the code.

Within a game, each player submits one prediction per race session: a 10th-place driver and a first-DNF driver. The two picks must be different drivers, and no two players in the same game can pick the same driver for the same position — uniqueness is enforced at the database level.

Predictions lock automatically at the official session start time. The game owner can manually override the first-DNF result after the race if the automatic detection is wrong.

---

## F1 data ingestion

Race data is sourced from the [Jolpica F1 API](https://github.com/jolpica/jolpica-f1), a community-maintained wrapper around the Ergast dataset.

Ingestion happens in two steps:

**1. Season setup** (once per season)

```bash
curl -X POST https://your-backend/f1/admin/setup/2026 \
  -H "x-admin-secret: your-secret"
```

Ingests the full season schedule, circuits, drivers, and constructors. Creates stub result rows for every session so drivers are available for predictions before results exist.

**2. Results ingestion** (after each race weekend)

```bash
curl -X POST https://your-backend/f1/admin/ingest/2026/results \
  -H "x-admin-secret: your-secret"
```

Ingests race and qualifying results for all completed sessions in the season. Safe to run multiple times — all operations are upserts.

Both endpoints are protected by the `X-Admin-Secret` header. In production, ingestion is triggered manually via GitHub Actions: **Actions → Ingest F1 Results → Run workflow**.

---

## Database migrations

The project uses Alembic for schema migrations.

```bash
cd backend

# Generate a migration after changing a model
uv run alembic revision --autogenerate -m "description"

# Apply pending migrations
uv run alembic upgrade head

# Check current state
uv run alembic current
```

Migration scripts live in `backend/alembic/versions/`.

---

## Email reminders

Prediction reminder emails are sent via [Resend](https://resend.com/). An APScheduler job runs every 30 minutes and checks whether any race session starts within the next hour. If one does, it emails all game members who have not yet submitted a prediction for that session.

To test email sending without waiting for the scheduler:

```bash
curl -X POST https://your-backend/f1/admin/trigger-reminders \
  -H "x-admin-secret: your-secret"
```

---

## Local development

**Prerequisites:** Python 3.11+, Node 18+, PostgreSQL, [uv](https://docs.astral.sh/uv/getting-started/installation/)

**Backend**

```bash
cd backend

# Install dependencies
uv sync

# Create .env
cp .env.example .env  # then fill in values

# Run migrations
uv run alembic upgrade head

# Start dev server
uv run python app/main.py
```

The API will be available at `http://localhost:8000`. Interactive docs at `/docs`.

**Environment variables:**

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT signing key (any random string) |
| `ADMIN_SECRET` | Secret for admin endpoints |
| `RESEND_API_KEY` | Resend API key for email |

**Frontend**

```bash
cd frontend
npm install

# Create .env.local
echo "VITE_API_URL=http://localhost:8000" > .env.local

npm run dev
```

---

## API reference

A [Bruno](https://www.usebruno.com/) collection covering all endpoints is included at `backend/bruno/`. Open the folder as a collection in Bruno to explore and test the API locally.

---

## Deployment

The production deployment uses:

- **Frontend:** [Vercel](https://vercel.com/) — connect the repo, set `VITE_API_URL` as an environment variable pointing to your backend URL, deploy from `frontend/`
- **Backend:** [Railway](https://railway.app/) or [Render](https://render.com/) — deploy from `backend/` using the included Dockerfile, set all environment variables in the platform dashboard
- **Database:** [Supabase](https://supabase.com/) or any managed PostgreSQL — copy the connection string to `DATABASE_URL`

CORS is locked to the production frontend origin in `backend/app/main.py`. Update `allow_origins` if your frontend URL changes.

**GitHub Actions**

Add two repository secrets:

| Secret | Value |
|---|---|
| `BACKEND_URL` | Your backend base URL |
| `ADMIN_SECRET` | Same value as backend `ADMIN_SECRET` |

Then trigger ingestion after each race weekend via **Actions → Ingest F1 Results → Run workflow**.
