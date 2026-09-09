# Execution PRD — Deepansha

## Responsibility
Frontend/dashboard, UI states, visualization, UX implementation.

## Deliverables
- `DEEPANSHA-001` Dashboard shell + mock data layer.
- `DEEPANSHA-002` Full dashboard per `design/dashboard-spec.md`.
- `DEEPANSHA-003` Real backend integration + demo polish.

## Interfaces depended on
`architecture/api-contract.md` and `architecture/data-model.md`; real API only from `KARTHI-005` onward.

## Interfaces provided
The dashboard and mock layer, which also validates that the shared API contract is usable.

## Acceptance criteria
FR-UI-1 through FR-UI-7 and the dashboard spec section-by-section.

## Integration strategy
Build against mocks before backend is ready. At P7 swap mocks for real API. If the real API requires shape changes, treat that as a contract/documentation defect rather than silently patching the frontend.

## Critical UI requirements
All 9 sections must exist, including explicit loading/empty/error states. No placeholder data should remain in the live demo.
