# Vortex_SICM Documentation

**Hackathon:** AAVISHKARA-26  
**Problem:** JP-012 — Customer Arrival Queue Simulation & Resource Allocation Optimizer  
**Domain:** Bank branch operations  
**Language:** Python (backend/simulation/optimization); frontend stack owned by Deepansha.

## What this project is
An explainable decision-support system for a bank branch operations manager:
synthetic data → demand forecast → queue simulation → resource allocation optimization → explainable recommendation → what-if simulation → baseline vs optimized comparison.

## Shared documentation map
- `requirements/` — PRD, functional requirements, non-functional requirements, acceptance criteria
- `architecture/` — architecture, domain model, data model, simulation design, optimization design, API contract, TRD
- `execution/` — phases, task board, dependency map, integration plan, definition of done, submission checklist
- `design/` — UX, dashboard specification, demo flow
- `testing/` — test strategy, test cases, validation checklist
- `decisions/` — ADR-001 through ADR-004
- `team/` — participant execution PRDs
- `risk-register.md` — known risks and mitigations
- `engineering-rules.md` — team workflow rules

`.chatgpt/HACKATHON_CONTEXT.md` remains orchestration memory only. It is not a coding-requirements source.

## Source-of-truth order
1. Official hackathon problem statement and event rules
2. Explicit human team instructions
3. Current repository implementation
4. `AGENTS.md` / `AI_INSTRUCTIONS.md`
5. This `docs/` tree
6. Engineering inference documented in ADRs
