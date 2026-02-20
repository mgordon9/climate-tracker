# Climate Globe — Project Spec

## Overview
A web application that displays an interactive 3D globe. Users can click on any country to view climate change data over time, ask natural language questions about climate trends, and see a real-time feed of related news articles.

## Application Goals
- Easily see climate change effects over time and easily verify data sources
- Easily see climate change causes/facotrs over time and easily verify data sources

## Learning Goals
- Learn Python/FastAPI by building a production-style backend
- Implement RAG with pgvector and an LLM API
- Build a real-time data pipeline with Kafka
- Containerize and deploy with Docker
- Have a portfolio project that demonstrates AI integration skills

---

## Tech Stack
- **Frontend:** React, TypeScript, react-globe.gl
- **Backend:** Python, FastAPI
- **Database:** PostgreSQL 16 + pgvector (via Docker Compose)
- **ORM:** SQLAlchemy 2.0 (sync)
- **Migrations:** Alembic
- **Package Manager:** Poetry
- **Streaming:** Kafka
- **AI/LLM:** TBD (decide in Phase 4)
- **Embedding Model:** Local, sentence-transformers (all-MiniLM-L6-v2)
- **Infrastructure:** Docker, Terraform
- **Cloud Provider:** AWS (single EC2 t3.small running Docker Compose, upgrade to t3.medium for Kafka phase)

---

## Data Sources
 - GHG emissions per capita by fuel type -- Our World in Data (CO2 & GHG Dataset)
 - forest area % -- Global Forest Watch
 - temperature --  World Bank Climate API
 - count, deaths, injuries, economic damage from global disasters per country -- EM-DAT (Disaster Database)

### News
- GDELT Project — https://api.gdeltproject.org/api/v2/doc/doc

### RAG Knowledge Base
All climate data sources and news articles listed above are ingested into pgvector for the Q&A system. This includes:
- All climate data from World Bank, Our World in Data, EM-DAT, Global Forest Watch, NOAA
- All news articles ingested via the news pipeline (GDELT, NewsAPI)
- IPCC report summaries
- Country-specific climate action plans

---

## Features

### Phase 1 — Project Setup & Data Model
- [ ] Initialize repo with FastAPI project structure
- [ ] PostgreSQL schema for countries, climate data points
- [ ] Basic API endpoints: list countries, get country detail
- [ ] Database seed script to load climate data
- [ ] pgvector extension enabled

### Phase 2 — Globe UI & Country Detail View
- [ ] Interactive 3D globe with clickable countries
- [ ] Country detail panel/page on click
- [ ] Display basic country info (name, region, population)
- [ ] Responsive layout
- [ ] Color countries by a climate metric (e.g. temperature change)

### Phase 3 — Climate Data & Visualizations
- [ ] Set up local embedding model (sentence-transformers, all-MiniLM-L6-v2)
- [ ] Ingest climate data from World Bank Climate API:
  - [ ] Store raw data in Postgres
  - [ ] Generate text descriptions (e.g. "Brazil's temperature rose 1.2°C since 1960")
  - [ ] Embed text descriptions, store vectors in pgvector
- [ ] Time-series charts temperature,
- [ ] Date range selector
- [ ] Compare country feature
- [ ] Data points to display per country:
  - [ ] Average temperature over time

### Phase 3.1 - Additional Climate Data Sources
- [ ] Ingest climate data (store raw data + generate text descriptions + embed into pgvector for each):
  - [ ] CO2 emissions over time per country -- Our World in Data
  - [ ] count, deaths, injuries, economic damage from global disasters per country -- EM-DAT (Disaster Database)
  - [ ] Deforestation rate per country -- Global Forest Watch
  - [ ] Sea level rise -- NOAA
  - [ ] Ocean temperature -- NOAA

### Phase 4 — RAG Q&A
- [ ] Ingest and embed IPCC report summaries and climate action plans
- [ ] Embed user questions, retrieve relevant chunks from all embedded data (climate data + documents + news articles)
- [ ] Send retrieved text + question to LLM API, return answer
- [ ] Chat UI component on country detail view
- [ ] Scope answers to selected country
- [ ] Show source references in answers

### Phase 5 — Real-Time News Pipeline (Celery)
- [ ] Set up Celery with Redis as broker
- [ ] Celery beat task: poll news source daily
- [ ] Celery worker task: embed articles, store in pgvector
- [ ] Celery worker task: classify articles by country using embeddings (or LLM)
- [ ] News feed component on country detail view
- [ ] SSE endpoint for live updates to connected browsers
- [ ] How often to poll for news: every day

### Phase 5.1 — Refactor News Pipeline to Kafka
- [ ] Replace Celery beat polling with Kafka producer
- [ ] Replace Celery worker tasks with Kafka consumers:
  - [ ] Consumer 1: embed articles, store in pgvector
  - [ ] Consumer 2: classify articles by country
  - [ ] Consumer 3: push updates via SSE to connected browsers
- [ ] Kafka topic for raw articles, separate topic for processed articles
- [ ] Handle consumer failures with Kafka offset management (replay capability)

### Phase 6 — Infrastructure & Deployment
- [ ] Dockerfile for each service (API, frontend, Kafka consumers)
- [ ] Docker Compose for local development
- [ ] Terraform config for cloud deployment
- [ ] CI/CD pipeline with GitHub Actions:
  - [ ] On PR: lint + run tests
  - [ ] On merge to main: build Docker images, push to container registry
  - [ ] On release/tag: deploy to cloud provider
- [ ] Target deployment: AWS EC2 t3.small with Docker Compose (upgrade to t3.medium when adding Kafka)

---

## UI/UX Notes
<!-- Describe any specific UI preferences, or write "no preference" -->
- Color scheme: No preference
- Globe style (realistic, minimal, dark theme): Realistic
- Layout: single page with panels
- Mobile support needed? yes
- Any design references or sites you like the look of: earth.google.com

---

## Scope Boundaries
<!-- What is explicitly NOT in v1? List things you want to avoid scope-creeping into -->
-
-
-

---

## Open Questions
<!-- Anything you're unsure about. I can help answer these before we start building -->
-
-
