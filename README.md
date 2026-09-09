# Vortex SICM — AAVISHKARA-26 · JP-012

**Bank Branch Operations Decision-Support Dashboard**

> A decision-support system that predicts customer demand, simulates multiple service queues, evaluates staffing, and recommends feasible resource allocation to reduce waiting time.

## Purpose

Vortex SICM helps a **bank branch operations manager** answer a practical operational question:

> **Given expected customer demand and limited staff, where should staff be allocated to keep queues under control and reduce waiting time?**

The application turns synthetic branch-demand scenarios into an explainable operational recommendation:

```text
Synthetic arrival/service data
        ↓
Demand forecast by time slot
        ↓
Multiple-queue simulation
        ↓
Baseline staffing allocation
        ↓
Feasible resource optimization
        ↓
Baseline vs optimized comparison
        ↓
Explainable recommendation
        ↓
What-if simulation
```

The product is **not** an autonomous agent and is **not** just a queue simulator. The deterministic simulation and optimization layer is the source of truth; the dashboard presents the resulting operational evidence to a human decision-maker.

## JP-012 requirements covered

The MVP is designed around the official JP-012 outcomes:

- Multiple service queues
- Waiting-time estimation
- Demand prediction by time slot
- Staff/resource allocation
- Overload identification
- Comparison with a basic allocation strategy
- Respect for resource limits
- Explainable recommendation logic
- Peak-load demonstration

All scenario data used by the project is synthetic or generated for the hackathon. No real bank/customer data is required.

## Current implementation

The repository currently contains the shared Python/FastAPI backend foundation and the core data, forecasting, simulation, optimization, API, and test modules. The remaining work is to validate the integrated behavior, complete frontend integration, and harden the end-to-end demo path.

Do not assume a feature is complete from its file existing alone. Use the task board, tests, current implementation, and actual execution results to determine completion.

## Quick setup

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
# Open http://localhost:8000/api/health → {"status":"ok"}
# Open http://localhost:8000/docs      → Swagger UI
```

## Run tests

```bash
pytest tests/ -v
```

Only report tests as passing after actually running them.

## Project structure

```text
Vortex_SICM/
├── backend/
│   ├── main.py                    # FastAPI application
│   ├── models.py                  # Shared Pydantic contracts
│   ├── simulation/
│   │   └── engine.py              # Queue simulation (KARTHI-003)
│   ├── forecasting/
│   │   └── forecast.py            # Demand forecast (KARTHI-004)
│   ├── optimization/
│   │   ├── baseline.py            # Basic allocation baseline (KIRAN-004)
│   │   ├── optimizer.py            # Feasible exhaustive optimizer (KIRAN-002)
│   │   └── explain.py              # Deterministic explanation (KIRAN-003)
│   └── routes/
│       ├── scenario.py             # Scenario generation API
│       ├── forecast.py             # Forecast API
│       ├── simulation.py           # Simulation/what-if APIs
│       └── optimization.py         # Optimization API
├── data/
│   ├── generator.py               # Synthetic data
│   └── scenarios.py               # Normal / Peak / Surge scenarios
├── frontend/                      # Operations dashboard
├── tests/                         # Unit/integration tests
├── docs/                          # Requirements, architecture, execution, design, testing
├── AGENTS.md                      # Coding-agent rules
├── AI_INSTRUCTIONS.md             # AI coding-assistant rules
├── requirements.txt
└── .env.example
```

## API surface

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Service liveness |
| POST | `/api/scenario/generate` | Generate a deterministic synthetic scenario |
| POST | `/api/forecast` | Forecast demand by queue and time slot |
| POST | `/api/simulate` | Simulate an allocation |
| POST | `/api/optimize` | Find the best feasible allocation |
| POST | `/api/whatif` | Evaluate a manually selected allocation |

The binding API contract is documented in [`docs/architecture/api-contract.md`](docs/architecture/api-contract.md).

## Team execution boundaries

| Team member | Primary responsibility | Task IDs |
|---|---|---|
| Karthi | Data, forecasting, simulation, backend API | KARTHI-001–005 |
| Kiran | Optimization, baseline, explainability, decision logic | KIRAN-001–004 |
| Reethu | QA, edge cases, scenario validation, integration validation | REETHU-001–004 |
| Deepansha | Dashboard, visualization, UX, frontend integration | DEEPANSHA-001–003 |

Ownership is a coordination boundary, not permission to overwrite another teammate's work. Read `AGENTS.md` and the relevant task/spec before editing.

## Development workflow

Use a short-lived feature branch for each coherent task:

```bash
git pull origin main
git checkout -b <task-id>-<short-description>
# implement + test
git add -p
git commit -m "[<TASK-ID>] <description>"
git push origin <task-id>-<short-description>
```

Keep `main` demoable. Re-read shared files before changing them because teammates may be working concurrently.

## Competition timing

The official rules define:

- Event: **9 Sep 2026, 10:00 AM → 10 Sep 2026, 2:00 PM**
- Development begins: **9 Sep 2026, 1:30 PM**
- Final submission/judging freeze: **10 Sep 2026, 7:00 AM**
- Presentations: **10 Sep 2026, 9:00 AM–12:30 PM**

The submitted state at 7:00 AM is the judging baseline. Do not plan on modifying the submitted version after the freeze.

## AI and competition integrity

AI-assisted development, internet research, GitHub, external APIs/cloud services, and open-source libraries are permitted by the participant rules. AI-generated implementation must still be understood, tested, and owned by registered team members.

Only registered team members may provide technical contributions. AI tools are not a substitute for an authorized human contributor.

AI usage must be disclosed in the required event format. Keep an accurate record of the AI tools used, team members using them, purpose, and brief description.

See:

- `AGENTS.md` — coding-agent operating rules and competition guardrails
- `AI_INSTRUCTIONS.md` — AI coding-assistant behavior and validation rules
- `docs/engineering-rules.md` — team engineering workflow
- `docs/README.md` — documentation map and authority model

## Scope discipline

P0 is the complete decision-support loop:

```text
Data → Forecast → Simulation → Allocation → Baseline Comparison
→ Explainable Recommendation → What-If
```

Do not add authentication, complex microservices, real bank integrations, real customer data, unnecessary cloud infrastructure, deep-learning-heavy forecasting, or autonomous operational agents before the P0 path is stable.

## Internal delivery targets

| Time | Milestone |
|---|---|
| 05:30 AM | Feature freeze |
| 06:00 AM | Final integration |
| 06:15 AM | Clean-clone verification |
| 06:30 AM | Final repository/PPT/deployment verification |
| 06:45 AM | Submission readiness |
| **07:00 AM** | **Official judging freeze** |

For the complete requirements and acceptance criteria, use the documents under `docs/`.
