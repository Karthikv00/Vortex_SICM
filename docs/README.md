# Vortex_SICM Documentation

**Hackathon:** AAVISHKARA-26  
**Problem:** JP-012 — Customer Arrival Queue Simulation & Resource Allocation Optimizer  
**Domain:** Bank branch operations  
**Language:** Python (backend/simulation/optimization/data); frontend uses the repository's selected web stack.

## Purpose

Vortex SICM is an explainable bank-branch operations decision-support system. It forecasts synthetic customer demand, simulates multiple service queues, evaluates limited staffing, compares a basic allocation with an optimized feasible allocation, explains the recommendation, and supports what-if analysis.

The primary P0 loop is:

`data → demand forecast → queue simulation → resource allocation → baseline comparison → explainable recommendation → what-if result`

## Documentation map

- `requirements/` — PRD, functional requirements, non-functional requirements, acceptance criteria
- `architecture/` — architecture, domain model, data model, simulation design, optimization design, API contract, TRD
- `execution/` — phases, task board, dependency map, integration plan, definition of done, submission checklist
- `design/` — UX, dashboard specification, demo flow
- `testing/` — test strategy, test cases, validation checklist
- `decisions/` — ADR-001 through ADR-004
- `team/` — participant execution PRDs
- `risk-register.md` — known risks and mitigations
- `engineering-rules.md` — team engineering workflow and competition guardrails

`AGENTS.md` is the repository-level coding-agent policy. `AI_INSTRUCTIONS.md` contains AI coding-assistant-specific operating rules. `.chatgpt/HACKATHON_CONTEXT.md` is ChatGPT-only orchestration state and is not a coding-requirements source.

## Authority model

### Requirements authority

1. Official AAVISHKARA-26 participant rules
2. Official JP-012 problem statement
3. Explicit human team instructions
4. `AGENTS.md` / `AI_INSTRUCTIONS.md` for repository and AI-assistant behavior
5. Approved project specifications under `docs/`
6. ADRs and engineering inference

### Implementation truth

The current repository is the source of truth for **what is actually implemented**. Documentation is the source of truth for **what is required/intended**. Do not treat a file's existence as proof that its behavior is complete; verify through code execution and tests.

## AI instruction boundary

Do not place coding-agent operating rules only in this file or in the public README. Keep them in `AGENTS.md` and `AI_INSTRUCTIONS.md`, with competition/workflow rules also reflected in the appropriate engineering/decision documents.

AI-assisted development is permitted by the event rules, but registered team members remain responsible for understanding, validating, testing, and presenting the resulting implementation. AI usage must be recorded for the required event disclosure.
