# Product Requirements Document (PRD)

## Problem
Bank branches routinely misallocate staff across service queues (teller, loans, account services, etc.). Managers react to overload after it's visible in the lobby, not before. There is no simple, explainable way to see projected demand, know a branch is about to be overloaded, and get a concrete, justified staffing recommendation.

## Target user
Bank branch operations manager, running a single branch, planning staff allocation for the day/shift.

## Product vision
A simulation-backed decision-support tool: feed it a branch's queues and staff, see current/predicted load, get an explainable reallocation recommendation, and see the measured improvement before committing to it.

## Goals
- Make overload visible before it happens.
- Produce a staffing recommendation with a stated, inspectable reason.
- Let the manager test manual what-if scenarios instantly.
- Show a clear, honest baseline-vs-optimized comparison.

## Non-goals
- Not a scheduling/payroll system.
- Not a real-time production monitoring system tied to real branch hardware.
- Not a general-purpose forecasting or optimization framework.
- Not an autonomous system — it recommends, a human decides.

## MVP scope (P0)
- Multiple service queues with synthetic arrival/service data.
- Normal, peak, and sudden-surge scenarios.
- Queue simulation producing waiting-time and utilization metrics.
- Simple demand forecast (time-of-day + scenario multiplier).
- Resource allocation optimizer over hard staff/queue constraints.
- Baseline vs optimized comparison with measurable improvement.
- Overload detection and explainable recommendation.
- Interactive what-if control.
- Single-page operations dashboard.

## P1 scope (only after P0 is stable)
- User-adjustable simulation parameters.
- Basic appointment modeling.
- Staff skill/queue compatibility constraints.
- CSV import of real-ish data.
- Scenario persistence across sessions.
- Additional analytics.

## Success metrics
- Optimizer reduces average and p95 wait time vs baseline on at least peak and surge scenarios without violating hard constraints.
- End-to-end demo runs deterministically with a fixed seed.
- A judge can understand why a recommendation was made from the explanation panel alone.

## Assumptions and constraints
- Synthetic data is acceptable; no real customer data is used or required.
- Single branch, single shift/day horizon is sufficient.
- Staff are interchangeable in the P0 constraint model.
- Python is required for backend/simulation/optimization.
- No required LLM dependency for optimizer operation.
- No auth, microservices, or real bank integrations for P0/P1.
