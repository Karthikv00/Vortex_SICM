# Vortex SICM

**Bank Branch Operations Decision-Support System**

Vortex SICM helps a branch operations manager decide how to allocate limited staff across multiple service queues. It combines synthetic demand generation, time-slot demand forecasting, queue simulation, feasible resource optimization, baseline comparison, explainable recommendations, stress testing, and what-if analysis.

## What the system does

```text
Scenario / custom workload
        ↓
Demand forecast
        ↓
Multi-queue simulation
        ↓
Baseline allocation
        ↓
Feasible optimization
        ↓
Baseline vs optimized comparison
        ↓
Explainable recommendation
        ↓
What-if / stress testing
```

The deterministic simulation and optimization layer is the source of truth. The frontend is a decision-support interface for a human operator; the system does not autonomously operate a bank branch.

## Current application scope

- Multiple queues for teller, loan, and customer-service workloads
- Built-in synthetic scenarios for normal, peak, and surge demand
- Custom workload input with automatic scenario/task classification
- Demand forecasting by queue and time slot
- Waiting-time and overload estimation
- Resource-constrained staff allocation
- Baseline-versus-optimized comparison
- Deterministic recommendation explanations
- What-if allocation analysis
- Branch stress testing and resilience analysis
- Scenario history and operational metrics
- FastAPI backend + React/Vite frontend
- Vercel-compatible frontend deployment configuration

All demonstration/customer data is synthetic. No real customer or bank data is required.

## Repository layout

```text
Vortex_SICM/
├── backend/       FastAPI API, domain models, forecasting, simulation, optimization
├── data/          Synthetic data generation and predefined scenarios
├── database/      SQL schema and persistence-related database assets
├── frontend/      React/Vite operations dashboard
├── docs/          Requirements, architecture, design, testing, execution, decisions
├── scripts/       Development/benchmark utilities
├── tests/         Backend and integration test suite
├── infra/         Local infrastructure configuration
├── AGENTS.md      Repository coding-agent rules
├── AI_INSTRUCTIONS.md
├── requirements.txt
├── pytest.ini
└── vercel.json
```

## Run locally

### Backend

```bash
python -m venv .venv

# Windows
.venv\\Scripts\\activate

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
uvicorn backend.main:app --reload --port 8000
```

Backend endpoints are available under `/api`; health check: `GET /api/health`. Swagger UI is available at `/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend uses the API service layer in `frontend/src/services/api.js`. Configure the API base URL using the frontend environment configuration expected by the deployed build.

## Tests

```bash
pytest tests/ -v
```

Run the tests before claiming a change is complete. For frontend changes, also run the frontend build:

```bash
cd frontend
npm run build
```

## Documentation

Start with [`docs/README.md`](docs/README.md). It maps requirements, architecture, execution, design, testing, and decision records. The repository implementation is the source of truth for what is actually implemented; specifications describe intended behavior.

## Development rules

- Keep `main` deployable and demoable.
- Make focused changes; do not introduce unnecessary infrastructure.
- Preserve API contracts unless the change explicitly requires one.
- Test backend behavior and build the frontend after relevant changes.
- Do not commit secrets, local environment files, generated dependencies, or empty placeholder files.
- Read `AGENTS.md` and `AI_INSTRUCTIONS.md` before making substantial repository changes.

## Project

**Hackathon:** AAVISHKARA-26  
**Problem:** JP-012 — Customer Arrival Queue Simulation & Resource Allocation Optimizer  
**Team:** Vortex
