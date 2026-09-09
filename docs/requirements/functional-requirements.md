# Functional Requirements

## Data (FR-DATA)
- FR-DATA-1: Generate synthetic customer arrival data per service queue, per time slot, for a configurable day.
- FR-DATA-2: Support `normal`, `peak`, `surge`, each with a distinct arrival-rate profile.
- FR-DATA-3: Generated data is reproducible given a fixed random seed.
- FR-DATA-4: Data generation is independent of API/UI and testable standalone.

## Forecasting (FR-FCST)
- FR-FCST-1: Predict expected arrivals per queue per slot using historical/synthetic input plus a time-of-day factor and scenario multiplier.
- FR-FCST-2: Output a structured `ForecastResult` consumable by simulation without transformation.
- FR-FCST-3: Degrade gracefully with a documented fallback if historical data is insufficient.

## Simulation (FR-SIM)
- FR-SIM-1: Simulate arrivals and service over a time horizon, producing per-slot and aggregate waiting-time metrics.
- FR-SIM-2: Compute average and p95 waiting time per queue and branch-wide.
- FR-SIM-3: Compute staff utilization per queue.
- FR-SIM-4: Flag overloaded time slots against a defined threshold.
- FR-SIM-5: Simulation is deterministic given the same seed and inputs.

## Optimization (FR-OPT)
- FR-OPT-1: Enumerate feasible staff allocations under total-staff and per-queue min/max constraints.
- FR-OPT-2: Score feasible allocations with a transparent weighted objective: wait, overload, utilization, reallocation cost.
- FR-OPT-3: Select the best-scoring feasible allocation; hard constraints are never violated.
- FR-OPT-4: Report baseline score alongside optimized score.
- FR-OPT-5: If no feasible allocation exists, report this explicitly rather than returning an invalid recommendation.

## Explainability (FR-EXP)
- FR-EXP-1: Every recommendation includes inputs considered, constraints applied, score breakdown, and a short natural-language reason.
- FR-EXP-2: Explanation generation does not require an LLM; an LLM may optionally rephrase the deterministic explanation.

## What-if (FR-WHATIF)
- FR-WHATIF-1: User can manually set a staff allocation and receive simulated metrics using the same simulation engine as the optimizer.
- FR-WHATIF-2: What-if results are directly comparable to optimizer output.

## API (FR-API)
- FR-API-1: `/api/health` returns service status.
- FR-API-2: `/api/scenario/generate` returns synthetic data for a requested scenario.
- FR-API-3: `/api/forecast` returns `ForecastResult`.
- FR-API-4: `/api/simulate` returns `SimulationResult`.
- FR-API-5: `/api/optimize` returns `OptimizationResult`.
- FR-API-6: `/api/whatif` accepts a manual allocation and returns its simulation result.
- FR-API-7: All endpoints validate input and return structured errors on invalid input.

## Dashboard (FR-UI)
- FR-UI-1: Show current branch/queue state.
- FR-UI-2: Show demand forecast and overload alerts.
- FR-UI-3: Show current vs recommended allocation.
- FR-UI-4: Show before/after metrics comparison.
- FR-UI-5: Provide what-if controls.
- FR-UI-6: Show an explanation panel.
- FR-UI-7: Handle loading, empty, and error states for every panel.
