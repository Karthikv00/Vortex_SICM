# Execution PRD — Kiran

## Responsibility
Optimization and product/AI direction, decision logic, explainability, and backend integration support.

## Deliverables
- `KIRAN-001` Optimization sizing analysis and scoring design.
- `KIRAN-002` Enumeration/scoring/tie-break optimizer.
- `KIRAN-003` Deterministic explanation generation.
- `KIRAN-004` Baseline allocation strategy + what-if logic.

## Interfaces depended on
`SimulationResult` from Karthi's simulation engine; `ScenarioConfig` and `ForecastResult` contracts.

## Interfaces provided
`optimize(scenario, forecast) -> OptimizationResult` and `explain(result) -> str`.

## Acceptance criteria
FR-OPT-1 through FR-OPT-5, FR-EXP-1/2, and FR-WHATIF baseline strategy requirements.

## Critical rules
Do not treat optimizer results as correct until validated against the real simulation engine. Explanations must be generated from actual computed numbers. Benchmark enumeration against real implementation counts and keep it under the 3-second NFR.
