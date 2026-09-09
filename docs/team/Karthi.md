# Execution PRD — Karthi

## Responsibility
Backend, simulation engine, data flow, API integration.

## Deliverables
- `KARTHI-001` Synthetic data generator.
- `KARTHI-002` Core domain models.
- `KARTHI-003` Time-step simulation engine — critical path.
- `KARTHI-004` Demand forecasting.
- `KARTHI-005` FastAPI endpoints.

## Interfaces depended on
`data-model.md`; Kiran's optimizer/explanation/what-if logic for optimize and what-if routes.

## Interfaces provided
`generate(scenario_config)`, `simulate(forecast, allocation) -> SimulationResult`, `forecast(scenario) -> ForecastResult`, and all API endpoints.

## Acceptance criteria
FR-DATA-1–4, FR-SIM-1–5, FR-FCST-1–3, FR-API-1–7.

## Testing
Data determinism, simulation correctness across scenarios and edge cases, and API contract tests.

## Critical risks
Escalate simulation delays early. Prevent API contract drift. Every random call must trace back to `ScenarioConfig.seed`.
