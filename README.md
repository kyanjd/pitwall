Backend for F1 prediction web app. Friends should be able to log in to a particular "game" where they can predict who comes 10th and who goes out first for an F1 race (for now).

### Structure
f1-predictions/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── deps.py
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   ├── session.py
│   │   │   └── init_db.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── game.py
│   │   │   ├── prediction.py
│   │   │   ├── score.py
│   │   │   └── race_result.py
│   │   ├── schemas/
│   │   │   ├── user.py
│   │   │   ├── game.py
│   │   │   ├── prediction.py
│   │   │   └── score.py
│   │   ├── crud/
│   │   │   ├── user.py
│   │   │   ├── game.py
│   │   │   ├── prediction.py
│   │   │   └── score.py
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── api.py
│   │   │       └── endpoints/
│   │   │           ├── auth.py
│   │   │           ├── games.py
│   │   │           ├── predictions.py
│   │   │           └── leaderboard.py
│   │   ├── services/
│   │   │   ├── scoring.py
│   │   │   └── f1_data.py
│   │   └── tasks/
│   │       └── update_results.py
│   ├── alembic/
│   ├── alembic.ini
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.ts
│   │   ├── pages/
│   │   ├── components/
│   │   ├── hooks/
│   │   └── types/
│   ├── public/
│   ├── package.json
│   └── vite.config.ts
│
├── .gitignore
├── README.md
└── docker-compose.yml

### Development plan
Models + migrations
CRUD functions
Core scoring logic
Auth (JWT)
API endpoints
Frontend
Hosting

### Commands
```uv run alembic revision --autogenerate -m "message"```

```uv run alembic upgrade head ```

```docker compose exec db sh -c 'export $(grep -v "^#" .env | xargs) && psql -U $POSTGRES_USER -d $POSTGRES_DB -c "\dt"'```
