# AI Coding Instructions

These instructions apply specifically to AI coding assistants working in this repository. They complement `AGENTS.md`.

## Authority

Follow this order:
1. Official AAVISHKARA-26 participant rules and official JP-012 problem statement
2. The user's explicit task
3. `AGENTS.md`
4. This `AI_INSTRUCTIONS.md`
5. Relevant project documentation under `docs/`
6. Existing implementation

If a conflict remains, stop and surface it. Do not silently invent a compromise.

## Required operating behavior

### Inspect before editing
- Inspect repository structure, current branch/status, relevant source files, docs, tests, and existing interfaces.
- Re-read shared files immediately before changing them; do not rely on an earlier snapshot.
- Check recent repository changes when teammates may be working concurrently.
- Identify the smallest coherent change that satisfies the requested task.
- Reuse existing behavior before introducing abstractions, dependencies, or duplicate implementations.

### Respect the agent boundary
- You are an implementation assistant, not the project orchestrator.
- Do not assign work to teammates.
- Do not infer teammate identity or ownership from names alone.
- Do not autonomously implement unrelated modules.
- If the user asks for an audit or plan, audit/plan first rather than coding.

## Competition guardrails

- AAVISHKARA-26 substantive development begins at **9 September 2026, 1:30 PM**. Before that time, only preparation such as inspection, planning, environment setup, and documentation review is permitted; do not implement the substantive JP-012 solution.
- The final submission/judging version freezes at **10 September 2026, 7:00 AM**. Do not plan or perform team-initiated source, repository, deployment, PPT, or judging-material changes after the freeze unless an organizer authorizes an exceptional intervention.
- The submitted solution must be genuinely developed during the competition. Do not import or substantially reuse a completed pre-existing solution.
- Framework starters, standard developer tooling, open-source libraries, internet research, GitHub, legitimate external APIs, and cloud services are permitted subject to the official event rules and applicable licenses.

## AI usage and human responsibility

AI-assisted development is allowed by the event rules, but:

- Only registered team members may provide technical contributions.
- AI tools do not count as a substitute for an authorized human contributor.
- The registered team member responsible for a change must understand, review, test, and accept AI-generated code before merge.
- Do not conceal external human contribution or use another person's account to disguise it.
- Maintain an accurate AI disclosure record: tool/service, team member using it, purpose, and brief description.
- Never misrepresent third-party or AI-generated work as original human-only work.

## Product and technical constraints

Project: **Vortex SICM — AAVISHKARA-26 JP-012**.

Purpose: provide an explainable decision-support workflow for a bank branch operations manager to forecast customer demand, simulate multiple queues, evaluate limited staffing, compare a basic allocation with an optimized feasible allocation, explain the recommendation, and run what-if scenarios.

Core loop:

`data → demand forecast → queue simulation → resource allocation → baseline comparison → explainable recommendation → what-if result`

The deterministic simulation/optimization layer is authoritative.

LLMs or external AI services may assist with optional explanation/UX polish, but must NOT be required for core correctness and must NOT be the source of truth for:

- demand forecasts
- queue state
- waiting-time metrics
- capacity calculations
- hard constraints
- allocation decisions
- benchmark results
- improvement metrics

## Data and integrity

- Use synthetic/self-created data for the MVP.
- Never commit real customer data, credentials, API keys, tokens, or secrets.
- Do not fabricate benchmark numbers or improvement metrics.
- Do not cherry-pick favorable measurements while hiding contradictory results.
- Baseline and optimized comparisons must use comparable inputs and simulation conditions.
- Every displayed performance number must be traceable to actual execution.

## P0 implementation scope

P0 is the complete judging path:

`Data → Forecast → Simulation → Allocation → Baseline Comparison → Explainable Recommendation → What-If`

P0 must support:

- multiple queues
- synthetic arrival/service data
- normal/peak/surge scenarios
- demand prediction by time slot
- waiting-time estimation
- overload detection
- feasible allocation under hard resource limits
- basic baseline allocation
- baseline vs optimized comparison
- explainable recommendations
- interactive what-if evaluation

Do not introduce P1 functionality before P0 is stable.

Avoid unless explicitly required after P0:

- authentication/RBAC
- microservices
- unnecessary cloud infrastructure
- real bank integrations
- real customer data
- deep-learning-heavy forecasting
- autonomous operational agents
- unnecessary dependencies

## Simulation and optimization rules

- Hard constraints must be enforced independently of objective scoring.
- Keep optimization deterministic and explainable.
- Current P0 strategy is exhaustive feasible-allocation enumeration at the intended small problem size.
- Do not add OR-Tools, scipy.optimize, metaheuristics, or another solver without a concrete measured requirement and human approval.
- Validate optimizer behavior against the real simulation engine.
- Define metric units explicitly.
- Keep baseline and optimized simulations comparable.
- Prefer deterministic seeded scenarios for tests and demonstrations.

## Coding standards

- Keep modules cohesive and interfaces explicit.
- Validate inputs at API/system boundaries.
- Handle expected failures with useful errors.
- Prefer the smallest correct implementation.
- Preserve stable API/data contracts unless the task explicitly changes them.
- If a contract changes, update direct consumers, focused tests, and relevant documentation.
- Do not modify unrelated files or perform broad formatting rewrites.
- Avoid duplicate implementations.

## Testing and verification

For non-trivial changes, add/update focused tests covering the affected behavior.

Prioritize:

- queue behavior and waiting-time calculations
- normal/peak/surge scenarios
- hard resource constraints
- invalid/infeasible inputs
- baseline vs optimized comparison
- deterministic outputs
- API contracts where applicable
- integration with the real simulation engine

Run focused tests first and broader checks when practical.

**Never say a test passed unless you actually ran it.**

If execution is unavailable, state that verification was not performed.

## Git and change discipline

- Keep `main` demoable.
- Prefer one short-lived feature branch per coherent task: `<task-id>-<short-description>`.
- Include task ID in commits.
- Do not force-push or rewrite shared history without explicit human instruction.
- Never overwrite teammate work from stale context.
- Keep commits small and reviewable.

## Handoff requirements

At the end of a meaningful change, report:

1. Files changed.
2. Functionality implemented.
3. Exact tests/commands run and their results.
4. Contract changes, if any.
5. Known limitations/assumptions.
6. Recommended next step.

Do not claim completion beyond what was actually implemented and verified.
