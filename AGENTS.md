# ShiftPilot — Agent Instructions

## Architecture

Monorepo with two main packages:

- `backend/` — Python FastAPI application with Google OR-Tools CP-SAT scheduling engine
- `frontend/` — Next.js 14+ (App Router) with TypeScript and Tailwind CSS

## Tech Stack

- **Backend**: Python 3.14, FastAPI, SQLAlchemy 2.0, Alembic, Google OR-Tools, JWT auth
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS v4, shadcn/ui components
- **Database**: SQLite for development (easily swappable to PostgreSQL)
- **Scheduling Engine**: Google OR-Tools CP-SAT solver (Python)

## Multi-Tenancy

Row-level isolation via `business_id` foreign key on every tenant-scoped table.
All queries must filter by the authenticated user's business_id.

## Conventions

### Backend
- Use Pydantic v2 models for request/response validation
- SQLAlchemy 2.0 style (mapped_column, Mapped types)
- Alembic for migrations — never modify schema directly
- REST API with versioned routes (`/api/v1/...`)
- Async endpoints where possible
- Proper HTTP status codes and error responses

### Frontend
- App Router with server components by default
- Client components only when interactivity needed (`"use client"`)
- Tailwind utility classes — no inline styles
- Follow taste-skill anti-slop design principles:
  - No generic gradient backgrounds
  - No icon-in-circle KPI cards
  - No "Welcome back" greetings
  - Type-driven hierarchy
  - Flat surfaces, hairline borders
  - Data-first colour usage
- Follow impeccable design craft principles

### General
- Environment variables via `.env` files (never commit secrets)
- Consistent naming: snake_case (Python), camelCase (TypeScript)
- Descriptive variable names — no single letters except loop indices

## Running the Project

```bash
# Backend
cd backend
pip install -r requirements.txt
alembic upgrade head
python -m uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

## Testing

```bash
# Backend tests
cd backend && pytest

# Frontend
cd frontend && npm run build
```
