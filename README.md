# Vortex SICM — AAVISHKARA-26 · JP-012

**Bank Branch Operations Decision-Support Dashboard**

> Customer Arrival Queue Simulation & Resource Allocation Optimizer

---

## Quick Setup (everyone does this first)

```bash
# 1. Clone
git clone https://github.com/Kiran-official/Vortex_SICM.git
cd Vortex_SICM

# 2. Create virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the backend
uvicorn backend.main:app --reload --port 8000

# 5. Verify it works
# Open http://localhost:8000/api/health → should return {"status":"ok"}
# Open http://localhost:8000/docs      → Swagger UI with all endpoints
```

---

## Run Tests

```bash
# From project root (with .venv active)
pytest tests/ -v
```

---

## Project Structure

```
Vortex_SICM/
├── backend/
│   ├── main.py                    # FastAPI app — uvicorn entry point
│   ├── models.py                  # Shared Pydantic contracts (everyone reads this)
│   ├── simulation/
│   │   └── engine.py              # Time-step queue simulation (KARTHI-003)
│   ├── forecasting/
│   │   └── forecast.py            # Demand forecast (KARTHI-004)
│   ├── optimization/
│   │   ├── baseline.py            # Baseline allocation strategy (KIRAN-004)
│   │   ├── optimizer.py           # Exhaustive optimizer (KIRAN-002)
│   │   └── explain.py             # Deterministic explanation (KIRAN-003)
│   └── routes/
│       ├── scenario.py            # POST /api/scenario/generate
│       ├── forecast.py            # POST /api/forecast
│       ├── simulation.py          # POST /api/simulate, /api/whatif
│       └── optimization.py        # POST /api/optimize
├── data/
│   ├── generator.py               # Synthetic arrival data (KARTHI-001)
│   └── scenarios.py               # Normal / Peak / Surge configs (KARTHI-001)
├── frontend/                      # Dashboard UI (DEEPANSHA-001 onward)
├── tests/
│   ├── conftest.py                # Shared fixtures
│   ├── test_models.py
│   ├── test_data.py
│   ├── test_simulation.py
│   ├── test_optimization.py
│   └── test_api.py
├── docs/                          # All specification documents
├── requirements.txt
└── .env.example
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET  | `/api/health` | Service liveness |
| POST | `/api/scenario/generate` | Generate synthetic scenario data |
| POST | `/api/forecast` | Demand forecast for a scenario |
| POST | `/api/simulate` | Run simulation for an allocation |
| POST | `/api/optimize` | Find optimal allocation (exhaustive) |
| POST | `/api/whatif` | Simulate a manual allocation |

Full contract: [`docs/architecture/api-contract.md`](docs/architecture/api-contract.md)

---

## Team Task Ownership

| Who | Tasks | Modules to work on |
|-----|-------|--------------------|
| **Karthi** | KARTHI-001–005 | `data/`, `backend/simulation/`, `backend/forecasting/`, `backend/routes/`, `backend/main.py` |
| **Kiran** | KIRAN-001–004 | `backend/optimization/` |
| **Reethu** | REETHU-001–004 | `tests/` |
| **Deepansha** | DEEPANSHA-001–003 | `frontend/` |

> **Do not edit another teammate's module without coordination.**
> Read [`AGENTS.md`](AGENTS.md) before making any changes.

---

## Shared Data Contracts

All modules speak through the types in `backend/models.py`:

- `ScenarioConfig` — branch + queue configuration
- `ForecastResult` — demand per queue per slot
- `AllocationPlan` — staff counts per queue
- `SimulationResult` — wait, utilization, overload metrics
- `OptimizationResult` — baseline vs optimized with explanation

**Treat changes to `models.py` as breaking changes** — update `docs/architecture/data-model.md` and notify the team.

---

## Git Workflow

```bash
# Always pull before starting work
git pull origin main

# Create your feature branch
git checkout -b karthi/simulation-engine   # or reethu/tests, deepansha/dashboard

# Commit small and often
git add -p
git commit -m "[KARTHI-003] implement simulation engine core"

# Push and open a PR to main
git push origin karthi/simulation-engine
```

---

## Internal Deadlines

| Time | Milestone |
|------|-----------|
| 05:30 AM | Feature freeze |
| 06:00 AM | Final integration |
| 06:15 AM | Clean-clone verify |
| **07:00 AM** | **Official judging freeze** |
