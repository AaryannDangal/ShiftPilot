# ShiftPilot

An intelligent workforce scheduling platform for restaurants, cafes, fast-food businesses, hotels, and retail stores.

## Architecture

This is a monorepo with two main packages:

- `backend/` — Python FastAPI application with Google OR-Tools CP-SAT scheduling engine
- `frontend/` — Next.js 14+ (App Router) with TypeScript and Tailwind CSS

## Quick Start

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

### Authentication

- `POST /api/v1/auth/register` — Register a new business and owner account
- `POST /api/v1/auth/login` — Login with email/password
- `GET /api/v1/auth/me` — Get current user
- `GET /api/v1/auth/business` — Get business details

### Employees

- `POST /api/v1/employees/` — Create employee
- `GET /api/v1/employees/` — List employees
- `POST /api/v1/employees/skills` — Create skill
- `GET /api/v1/employees/skills` — List skills

### Scheduling

- `POST /api/v1/scheduling/generate` — Generate optimized schedule using OR-Tools
- `GET /api/v1/scheduling/schedules` — List schedules
- `POST /api/v1/scheduling/schedules/{id}/publish` — Publish a schedule

## Database Models

### Core Entities

- `Business` — Multi-tenant organization
- `Location` — Physical location within a business
- `User` — Authentication user with role (owner/manager/employee)
- `Employee` — Team member with employment details
- `Skill` — Qualification/skill that employees may have
- `Availability` — Daily availability for each employee
- `LeaveRequest` — Time-off request with approval workflow
- `Shift` — Scheduled work period
- `Schedule` — Weekly/monthly schedule grouping shifts
- `StaffingRequirement` — Staffing levels per day/time

## Scheduling Engine

The `app/services/scheduler.py` uses Google OR-Tools CP-SAT to solve scheduling optimization with:

**Hard Constraints:**
- Employee availability
- Contractual working-hour limits
- Leave approvals
- Skill qualifications
- Staffing minimums
- Rest period requirements

**Soft Constraints (configurable weights):**
- Shift preferences
- Weekend distribution fairness
- Opening/closing shift balance
- Labor cost minimization

## Testing

```bash
# Backend tests
cd backend
PYTHONPATH=. pytest app/tests/ -v

# Frontend build check
cd frontend
npm run build
```

## Environment Variables

Create a `.env` file in the backend root:

```
SHIFTPILLOT_SECRET_KEY=your-secret-key-here
SHIFTPILLOT_DATABASE_URL=sqlite:///./shiftpilot.db
SHIFTPILLOT_ACCESS_TOKEN_EXPIRES_MINUTES=1440
SHIFTPILLOT_BACKEND_CORS_ORIGINS=http://localhost:3000
```

## License

MIT

## Docker Production Deployment

To run the entire application stack using Docker Compose:

```bash
docker-compose up --build
```

- **Backend API**: `http://localhost:8000`
- **Frontend App**: `http://localhost:3000`
- **API Docs (Swagger)**: `http://localhost:8000/docs`
