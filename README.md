# Pitwall

A prediction game for F1 enjoyers — upgrade to the manual version played for a few seasons.

Each race, every player picks who they think will finish 10th and who will DNF first. Points are awarded based on how close the 10th-place pick was and whether the DNF call was correct. Predictions lock at the official session start time, and each driver pick is first-come-first-serve.

**Live:** https://pitwall-tau.vercel.app

---

## How scoring works

Each race scores two predictions:

**10th place** — points scale with how far off the pick was (same system as F1 races):

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
- [PostgreSQL](https://www.postgresql.org/) via [Supabase](https://supabase.com/)
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
      api/            # FastAPI route handlers, dependency injection
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

Authentication uses JWT bearer tokens (HS256) with no refresh token flow — the access token is long-lived and stored in `localStorage`. Passwords are hashed with bcrypt. Login follows the OAuth2 password flow, returning a bearer token used on all subsequent requests.

---

## Games

A game is tied to a specific F1 season. The owner creates it and shares a 6-character invite code with friends. Within a game, each player submits one prediction per race: a 10th-place driver and a first-DNF driver. The two picks must be different drivers, and no two players in the same game can select the same driver for the same position — uniqueness is enforced at the database level.

Predictions lock automatically at the official session start time. The game owner can manually override the first-DNF result if the automatic detection from the results data is wrong. Qualifying results are shown when available to aid with predictions, and race results are shown afterwards.

---

## F1 data ingestion

Race data is sourced from the [Jolpica F1 API](https://github.com/jolpica/jolpica-f1), a community-maintained Ergast wrapper. Ingestion runs in two steps: a one-time season setup that pulls the schedule, circuits, drivers, and constructors; and a post-race results ingest that pulls finishing positions and statuses for all completed sessions. All operations are upserts, so the results ingest can be run safely multiple times.

Both ingest endpoints are protected by an `X-Admin-Secret` header. In production, they are triggered manually via a GitHub Actions `workflow_dispatch` after each race weekend — no cron schedule, since race times are not fixed.

TODO: schedule on race completion.

---

## Database migrations

The project started with `SQLModel.metadata.create_all` for convenience during early development, which turned into a database creation/update cli tool. Now that players are actively using it, Alembic handles all schema changes using migrations to avoid data loss.

---

## Email reminders

An APScheduler job runs every 30 minutes and checks whether any race session starts within the next hour. If one does, it queries for game members who have not yet submitted a prediction and sends them a reminder via Resend. There is also an admin endpoint to trigger the job immediately for testing.

---

## API reference

A [Bruno](https://www.usebruno.com/) collection covering the important endpoints is included at `backend/bruno/` (mainly used during development).

TODO: move from manual Bruno collection running to API test suite.

---

## Deployment

- **Frontend** — deployed on [Vercel](https://vercel.com/), built from `frontend/`
- **Backend** — deployed on [Render](https://render.com) via the included Dockerfile
- **Database** — [Supabase](https://supabase.com/) managed PostgreSQL

CORS is locked to the production Vercel domain. Post-race result ingestion is triggered manually via GitHub Actions using secrets for the backend URL and admin key.
