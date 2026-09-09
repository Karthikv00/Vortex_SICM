# Task Board

Use task IDs in commits and Slack `[CHANGE]` posts. Ownership is a starting responsibility boundary; unblocked work may be picked up by others with coordination.

## Karthi
- **KARTHI-001:** Synthetic data generator — `data/generator.py`, `data/scenarios.py`; deterministic normal/peak/surge; 3–4h.
- **KARTHI-002:** Core domain models — `backend/models.py`; exact shared schema, typed and serializable; 2h.
- **KARTHI-003:** Time-step simulation — `backend/simulation/engine.py`; depends on models; critical path; 5–6h.
- **KARTHI-004:** Demand forecasting — `backend/forecasting/forecast.py`; time-of-day × scenario multiplier; 3h.
- **KARTHI-005:** FastAPI endpoints — `backend/main.py`, `backend/routes/`; exact API contract; 4h.

## Kiran
- **KIRAN-001:** Enumeration sizing benchmark + scoring validation; measure real implementation counts/runtime and finalize ADR-004. **NEXT TASK.**
- **KIRAN-002:** Enumeration/scoring/tie-break optimizer — `backend/optimization/optimizer.py`; implementation present; correctness/performance validation required.
- **KIRAN-003:** Deterministic explanation generation — `backend/optimization/explain.py`; implementation present; validate against actual computed numbers.
- **KIRAN-004:** Baseline strategy + what-if logic — `backend/optimization/baseline.py` and route contribution; implementation present; validate against current API/simulation contracts.

## Reethu
- **REETHU-001:** Test scaffolding and first generator tests; 2h.
- **REETHU-002:** Edge-case/scenario validation suite; 4–5h spread across phases.
- **REETHU-003:** Demo scenario realism + validation; 2–3h.
- **REETHU-004:** Ongoing documentation/code drift monitoring.

## Deepansha
- **DEEPANSHA-001:** Dashboard shell + mock API layer; all 9 sections; 4h.
- **DEEPANSHA-002:** Full dashboard per spec, including loading/empty/error states; 6–8h.
- **DEEPANSHA-003:** Real API integration + demo polish; 3–4h.

## Current coordination state
The foundation code is now on `main`, including data/forecasting/simulation/optimization/API modules and a first test suite. Do not assume all of those implementations have passed local execution; each owner must verify their path with actual runs.

**Kiran's immediate dependency:** validate `KIRAN-002`/`KIRAN-003`/`KIRAN-004` against the real current simulation/API implementation through `KIRAN-001` before further optimization feature work.
