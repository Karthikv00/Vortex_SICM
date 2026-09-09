# AAVISHKARA-26 — ChatGPT Orchestration State

> **ChatGPT-only state.** This file is for orchestration across conversations, not coding instructions. Coding agents must follow the user's task, official event rules/problem statement, `AGENTS.md`, `AI_INSTRUCTIONS.md`, project docs, and existing code.

## 1. Event constraints
- Hackathon: AAVISHKARA-26.
- Official event: 2026-09-09 10:00 → 2026-09-10 14:00.
- Development starts: 2026-09-09 13:30.
- Judging-version freeze: 2026-09-10 07:00. No team-initiated modification after freeze.
- Presentation: 09:00–12:30; target ~10–12 min: 5 min PPT + 3 min demo + 2 min Q&A/setup.
- AI assistance, internet, GitHub, external APIs/cloud, and open-source libraries are allowed; AI usage must be disclosed.
- Only registered team members may contribute technical work.

## 2. Team / collaboration
- Registered members: Kiran, Karthi, Reethu, Deepansha.
- All four can work simultaneously on the same GitHub repository and have their own laptops.
- Team is beginner-level; instructions and interfaces must be concrete and independently verifiable.
- Do not infer identity/ownership from names or roles when delegating to coding agents.

## 3. Selected problem
**JP-012 — Customer Arrival Queue Simulation & Resource Allocation Optimizer**

Domain: **bank branch operations**.

Required outcome:
`arrival/service data → demand prediction → multiple queues → waiting-time estimation → resource allocation → overload detection → baseline comparison → explainable recommendation`.

Hard requirements to preserve:
- resource limits/constraints
- peak-load demonstration
- explainable recommendation logic
- comparison with a basic allocation strategy
- measurable waiting-time improvement

## 4. Product decision
Working concept: **bank branch operations decision-support dashboard**.
Primary user: branch operations manager.

Purpose: forecast synthetic customer demand, simulate multiple queues, evaluate limited staffing, compare basic and optimized feasible allocations, explain the recommendation, and support what-if analysis.

Demo story:
1. Show current branch state.
2. Select normal/peak/surge scenario.
3. Predict demand and identify overload.
4. Recommend feasible staff/resource reallocation.
5. Run what-if simulation.
6. Compare baseline vs optimized metrics.
7. Explain the recommendation and constraints.

The product is **not** merely a queue simulator and not an autonomous agent.

## 5. Technical decisions
- Python required for backend/simulation/optimization/data work.
- FastAPI is the preferred backend.
- Frontend should use the repository's selected web stack; avoid framework changes without a concrete reason.
- Deterministic/stochastic simulation + transparent constraint/scoring logic are the source of truth.
- Forecasting should be simple and explainable; synthetic data is acceptable.
- LLM use is optional and limited to explanation/UX assistance. Core forecasts, queue metrics, constraints, and allocation decisions must work without an LLM.
- MVP database/persistence is optional; do not add it unless it materially improves the demo.

## 6. Scope priority
### P0 — must work
- multiple bank service queues
- synthetic arrival/service data
- normal/peak/surge scenarios
- demand forecast
- queue simulation + waiting metrics
- feasible resource allocation optimization
- baseline fixed/basic allocation
- before/after comparison
- explainable recommendation
- interactive what-if result
- clear operations dashboard

### P1 — only after P0 is stable
- adjustable parameters
- scenario persistence
- richer appointments
- staff skill compatibility
- CSV import

### Avoid unless P0 is finished and there is a demonstrated need
- authentication/RBAC
- microservices
- real bank integrations/customer data
- complex cloud infrastructure
- deep-learning-heavy forecasting
- autonomous operational agents

## 7. Repository
Repo: `Kiran-official/Vortex_SICM`, default branch `main`.

Current repository contains the shared planning pack plus a foundation implementation covering data generation, domain models, forecasting, simulation, optimization, FastAPI routes, and tests. The frontend remains the major product-surface dependency.

## 8. Agent/instruction state
- `AGENTS.md`: repository coding-agent policy, competition timing/new-project restrictions, AI/human responsibility, engineering rules, P0 scope, testing, integration, and handoff requirements.
- `AI_INSTRUCTIONS.md`: AI coding-assistant-specific behavior, competition guardrails, AI disclosure/human validation requirements, deterministic-core rules, testing, and change discipline.
- `docs/engineering-rules.md`: team workflow, competition integrity, product engineering, and coordination rules.
- `docs/README.md`: documentation map, authority model, and AI instruction boundary.
- `.chatgpt/HACKATHON_CONTEXT.md`: orchestration state only; not coding guidance.

## 9. Current implementation state
- Planning specification pack: synced to `main`.
- Foundation implementation: present on `main`.
- Optimization implementation present: `backend/optimization/baseline.py`, `optimizer.py`, `explain.py`.
- Optimization tests present: `tests/test_optimization.py`.
- Simulation implementation present: `backend/simulation/engine.py`.
- API implementation present: `backend/main.py` and `backend/routes/`.
- Frontend implementation state must be checked before planning frontend-dependent work.
- Local execution/test status has **not** been independently verified in this ChatGPT session; do not claim the current suite passes.

## 10. Immediate Kiran task
**KIRAN-001 — Enumeration sizing benchmark + scoring validation.**

Kiran should:
1. Pull/re-read current `main`.
2. Run existing optimization tests.
3. Benchmark real normal/peak/surge scenarios.
4. Measure feasible allocation count, simulation runtime, optimizer runtime, baseline/optimized metrics, and constraint compliance.
5. Verify deterministic output.
6. Confirm the documented `<3 second` optimization target for intended MVP sizing.
7. Update ADR-004 with actual measurements.
8. Fix concrete defects discovered by tests/benchmark only.

Do not fabricate or cherry-pick favorable metrics. If execution is unavailable, record that verification was not performed.

## 11. Synchronization protocol
The repository is the source of truth for implementation state. This file is the source of truth for ChatGPT's cross-conversation orchestration state.

Before every substantive project response/action, re-check current repository state when repository changes may have occurred. Do not rely on an old snapshot of code or file contents.

When another team member/agent makes changes:
1. Inspect current `main` state and recent commits/diffs.
2. Determine what changed and whether architecture/interfaces/tests are affected.
3. Update this file's project state/decisions/risks as needed.
4. Only then plan or implement the next change.

This synchronization cannot be triggered invisibly by GitHub changes between messages. If a change happens outside the current interaction, the next project interaction must begin with a repository re-sync; never assume the previous context is still current.

## 12. Decision discipline
For every feature, ask:
- Does it directly improve the JP-012 judging outcome?
- Is it necessary for the P0 demo path?
- Can it be deterministic, explainable, and tested?
- Does it introduce avoidable integration risk for four concurrent contributors?

Prefer a smaller complete system over a larger incomplete system.
