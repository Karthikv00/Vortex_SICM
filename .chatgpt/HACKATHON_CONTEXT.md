# AAVISHKARA-26 — ChatGPT Orchestration State

> **ChatGPT-only state.** This file is for orchestration across conversations, not coding instructions. Coding agents must follow the user's task, `AGENTS.md`, project docs, and existing code.

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

Current structure includes `.chatgpt/`, `ai/`, `assets/`, `backend/`, `data/`, `database/`, `docs/`, `frontend/`, `infra/`, `scripts/`, `tests/`, `AI_INSTRUCTIONS.md`, `AGENTS.md`, and `README.md`.

Planning baseline was a universal hackathon boilerplate; no application implementation had been started at that point.

## 8. Agentic instruction state
- `AGENTS.md`: strengthened with instruction priority, project constraints, agent boundary, pre-edit inspection, engineering rules, test requirements, integration discipline, and hackathon integrity.
- `AI_INSTRUCTIONS.md`: aligned with the same constraints, including deterministic core logic, explainability, metric discipline, focused testing, and stale-context protection.
- `.chatgpt/HACKATHON_CONTEXT.md`: this orchestration snapshot; **not** coding guidance.

## 9. Synchronization protocol — important
The repository is the source of truth for implementation state. The context file is the source of truth for ChatGPT's cross-conversation orchestration state.

**Before every substantive response/action in this project, ChatGPT should re-check the current repository state when repository changes may have occurred.** Do not rely on an old snapshot of code or file contents.

When another team member/agent makes changes:
1. Inspect current `main` state and recent commits/diffs.
2. Determine what changed and whether architecture/interfaces/tests are affected.
3. Update this file's project state/decisions/risks as needed.
4. Only then plan or implement the next change.

This synchronization cannot be triggered invisibly by GitHub changes between messages. If a change happens outside the current interaction, the next project interaction must begin with a repository re-sync; never assume the previous context is still current.

## 10. Current implementation state
- Application code: **not yet started** at the planning snapshot.
- Agent/instruction hardening: complete.
- Latest verified repository state before this context update: commit `b7dfb34f08885a6c857227c472cb92bb56a4b781` (`AI_INSTRUCTIONS.md` alignment).
- Next step: inspect current docs/boilerplate, lock the minimal architecture/contracts, then build the smallest end-to-end P0 vertical slice.

## 11. Decision discipline
For every feature, ask:
- Does it directly improve the JP-012 judging outcome?
- Is it necessary for the P0 demo path?
- Can it be deterministic, explainable, and tested?
- Does it introduce avoidable integration risk for four concurrent contributors?

Prefer a smaller complete system over a larger incomplete system.
