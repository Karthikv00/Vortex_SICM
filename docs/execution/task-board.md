# Task Board

Use task IDs in commits and Slack `[CHANGE]` posts. Ownership is a starting responsibility boundary; unblocked work may be picked up by others with coordination.

## Karthi
- **KARTHI-001:** Synthetic data generator — `data/generator.py`, `data/scenarios.py`; deterministic normal/peak/surge. *(Completed & merged — PR #5)*
- **KARTHI-002:** Core domain models — `backend/models.py`; exact shared schema, typed and serializable. *(Completed & merged — PR #7)*
- **KARTHI-003:** Time-step simulation — `backend/simulation/engine.py`; depends on models; critical path. *(Completed & merged — PR #10)*
- **KARTHI-004:** Demand forecasting — `backend/forecasting/forecast.py`; time-of-day × scenario multiplier. *(Completed & merged — PR #13)*
- **KARTHI-005:** FastAPI endpoints — `backend/main.py`, `backend/routes/`; exact API contract. *(Completed & merged — PR #8, #9)*

## Kiran
- **KIRAN-001:** Enumeration sizing benchmark + scoring validation; measured real implementation counts/runtime and finalized ADR-004. *(Completed & merged — PR #4)*
- **KIRAN-002:** Enumeration/scoring/tie-break optimizer — `backend/optimization/optimizer.py`; validated against real simulation and benchmarked. *(Completed & merged)*
- **KIRAN-003:** Deterministic explanation generation — `backend/optimization/explain.py`; validated against actual computed numbers. *(Completed & merged)*
- **KIRAN-004:** Baseline strategy + what-if logic — `backend/optimization/baseline.py` and route contribution; validated against contracts. *(Completed & merged)*

## Reethu
- **REETHU-001:** Test scaffolding and first generator tests; `tests/test_reethu_001_generator.py`. *(Completed & merged — PR #6)*
- **REETHU-002:** Edge-case and scenario validation suite; `tests/test_reethu_002_*.py`. *(Completed & merged — PR #15)*
- **REETHU-003:** Demo scenario realism and validation; `tests/test_reethu_003_demo_scenarios.py`. *(Completed & merged — PR #11, #14)*
- **REETHU-004:** Ongoing documentation/code drift monitoring. *(Completed & merged — PR #17)*
- **REETHU-P8:** Pre-demo end-to-end integration and quality validation; `tests/test_reethu_p8_integration.py`, `docs/testing/validation-checklist.md`. *(Completed — PR ready)*

## Deepansha
- **DEEPANSHA-001:** Dashboard shell + mock API layer; all 9 sections; `frontend/`. *(In progress / active branch)*
- **DEEPANSHA-002:** Full dashboard per spec, including loading/empty/error states.
- **DEEPANSHA-003:** Real API integration + demo polish.

## Current coordination state
All backend foundation, simulation, optimization, forecasting, API routes, decision pipeline, and comprehensive test suites (231 tests passing) are completed and validated.

**Current priorities:**
1. Deepansha completing dashboard sections and real API integration (`DEEPANSHA-001` / `DEEPANSHA-002`).
2. Reethu finalizing Phase P8 integration validation and pre-demo checklist sign-off.

