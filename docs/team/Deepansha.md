# Execution PRD — Deepansha

## Responsibility
Frontend/dashboard, UI states, visualization, UX implementation, and real backend integration.

## Completed/planned deliverables
- `DEEPANSHA-001` Dashboard shell + initial mock data layer. *(Foundation/active integration work)*
- `DEEPANSHA-002` Full dashboard per approved design, including loading/empty/error states. *(Active)*
- `DEEPANSHA-003` Real FastAPI integration + demo polish. *(Current priority)*

## Backend integration baseline
The backend is now ready for real consumption. Latest main includes KIRAN-003 API/DecisionPipeline hardening (PR #20) and Reethu's pre-demo integration validation (PR #19). Karthi reports 231/231 backend tests passing, deterministic Normal/Peak/Surge pipelines, hard-constraint validation, real-simulator optimizer validation, and sub-50 ms average end-to-end runtimes for the canonical scenarios.

The dashboard must consume the existing API/data contracts rather than reproduce backend logic.

## DEEPANSHA-003 current objective
Replace all final/demo mock or hard-coded result paths with real FastAPI responses.

Required flow:
`dashboard controls → FastAPI → DecisionPipeline → real result → dashboard visualization`

Required visible results:
- scenario selection: Normal / Peak / Surge
- real forecast output
- baseline vs optimized allocation/results
- waiting-time metrics
- overload/backlog/utilization metrics where supplied by the API
- measured before/after improvement
- deterministic recommendation/explanation
- what-if result through the real backend where supported

Required UI states:
- loading
- successful result
- API/server error
- invalid/empty result
- retry/recovery path

## Integration rules
- No mock data in the final/demo execution path.
- Do not put simulation, forecasting, optimization, or KPI calculations in frontend code.
- Reuse the current API/data contracts. If a required response field is missing, coordinate with Kiran rather than silently inventing a frontend calculation.
- Verify locally against a running FastAPI instance using real responses.
- Keep the demo story focused: **problem → forecast → bottleneck → recommendation → measurable impact → what-if**.
- Avoid unnecessary frontend architecture changes.

## Current acceptance gate
A judge must be able to select a scenario and see real backend-generated forecast, simulation, optimization, comparison, and explanation results without changing code or injecting data. Reethu's integrated QA/clean-clone validation follows once the real dashboard path is ready.
