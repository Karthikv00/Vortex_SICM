# Task Board

Use task IDs in commits and Slack `[CHANGE]` posts. Ownership is a starting responsibility boundary; unblocked work may be picked up by others with coordination.

## Karthi
- **KARTHI-001:** Synthetic data generator — `data/generator.py`, `data/scenarios.py`; deterministic normal/peak/surge; 3–4h.
- **KARTHI-002:** Core domain models — `backend/models.py`; exact shared schema, typed and serializable; 2h.
- **KARTHI-003:** Time-step simulation — `backend/simulation/engine.py`; depends on models; critical path; 5–6h.
- **KARTHI-004:** Demand forecasting — `backend/forecasting/forecast.py`; time-of-day × scenario multiplier; 3h.
- **KARTHI-005:** FastAPI endpoints — `backend/main.py`, `backend/routes/`; exact API contract; 4h.

## Kiran
- **KIRAN-001:** Enumeration sizing benchmark + scoring design; finalize ADR-004 with measured numbers; 2–3h.
- **KIRAN-002:** Optimizer enumeration/scoring/tie-break — `backend/optimization/optimizer.py`; blocked by correct simulation; 5h.
- **KIRAN-003:** Deterministic explanation generation — `backend/optimization/explain.py`; traceable to computed numbers; 2h.
- **KIRAN-004:** Baseline strategy + what-if logic — `backend/optimization/baseline.py` and route contribution; 2h.

## Reethu
- **REETHU-001:** Test scaffolding and first generator tests; 2h.
- **REETHU-002:** Edge-case/scenario validation suite; 4–5h spread across phases.
- **REETHU-003:** Demo scenario realism + validation; 2–3h.
- **REETHU-004:** Ongoing documentation/code drift monitoring.

## Deepansha
- **DEEPANSHA-001:** Dashboard shell + mock API layer; all 9 sections; 4h.
- **DEEPANSHA-002:** Full dashboard per spec, including loading/empty/error states; 6–8h.
- **DEEPANSHA-003:** Real API integration + demo polish; 3–4h.

## Immediate parallel start
KARTHI-001, KARTHI-002, REETHU-001, and DEEPANSHA-001 can begin in parallel. Kiran can perform KIRAN-001 design/benchmark preparation but must validate optimizer correctness against the real simulation engine.
