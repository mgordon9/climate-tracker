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

## Data Sources

| Data | Source |
|---|---|
| Temperature change, CO₂ emissions, CO₂ per capita, methane | [Our World in Data — CO2 and GHG Emissions dataset](https://github.com/owid/co2-data) |
| Forest area (% of land area) | [World Bank Development Indicators — AG.LND.FRST.ZS](https://data.worldbank.org/indicator/AG.LND.FRST.ZS) (via FAO) |
| Global ocean SST anomaly | [NOAA Climate at a Glance — Global Ocean Surface Temperature](https://www.ncei.noaa.gov/cag/global/time-series) |
| Global mean sea level rise | [NOAA Laboratory for Satellite Altimetry — TOPEX/Jason altimetry](https://www.star.nesdis.noaa.gov/socd/lsa/SeaLevelRise/) |
| Disaster count, deaths, economic damage | [EM-DAT — The International Disaster Database](https://www.emdat.be/) (requires free registration; save export to `.data/emdat.csv`) |
| Country boundaries (globe polygons) | [Natural Earth](https://www.naturalearthdata.com/) via [world-atlas](https://github.com/topojson/world-atlas) |
| Country ISO codes (ISO 3166-1) | [i18n-iso-countries](https://github.com/michaelwittig/node-i18n-iso-countries) |

## Roadmap

See [docs/spec.md](docs/spec.md) for the full phase-by-phase plan.
