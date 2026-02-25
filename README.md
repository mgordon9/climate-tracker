# Climate Globe

An interactive 3D globe showing climate change data by country. Click any country to view temperature change, CO2 emissions, and other climate metrics over time.

## Tech Stack

- **Frontend:** React, TypeScript, Vite, react-globe.gl
- **Backend:** Python, FastAPI
- **Database:** PostgreSQL 16 + pgvector (Docker)
- **ORM/Migrations:** SQLAlchemy 2.0, Alembic
- **Package Manager:** Poetry

## Prerequisites

- Docker (via Colima or Docker Desktop)
- Node.js + npm
- Python 3.11
- Poetry (`pip3.11 install poetry`)

## Dev Setup

### 1. Install dependencies

```bash
# Backend
poetry install

# Frontend
cd frontend && npm install
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env if needed (default values work for local dev)
```

### 3. Start the database

If you have a local PostgreSQL brew service running, stop it first to avoid a port conflict:

```bash
brew services stop postgresql@14
```

Then start the Docker database:

```bash
docker compose up -d
```

### 4. Run migrations and seed data

```bash
poetry run alembic upgrade head
poetry run python scripts/seed.py
```

### 5. Start the backend

```bash
poetry run uvicorn app.main:app --reload
# API running at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### 6. Start the frontend

```bash
cd frontend && npm run dev
# App running at http://localhost:5173
```

## Project Structure

```
climate-tracker/
├── app/                  # FastAPI backend
│   ├── api/              # Route handlers
│   ├── models/           # SQLAlchemy models
│   ├── schemas/          # Pydantic schemas
│   └── main.py
├── alembic/              # Database migrations
├── scripts/              # Seed scripts
├── frontend/             # Vite + React frontend
│   └── src/
│       ├── components/   # Globe, CountryPanel
│       └── api.ts        # Typed fetch wrappers
├── docs/
│   └── spec.md           # Full project spec and roadmap
└── docker-compose.yml
```

## Roadmap

See [docs/spec.md](docs/spec.md) for the full phase-by-phase plan.
