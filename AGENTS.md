# Coding Agent Instructions

These instructions govern AI/coding assistants working in this repository. They are repository-level engineering and competition guardrails; they do not replace an explicit human task or the official event rules.

## Instruction priority
Follow this order:
1. Official AAVISHKARA-26 rules and official JP-012 problem statement
2. The user's explicit task in the current conversation
3. This `AGENTS.md`
4. `AI_INSTRUCTIONS.md` for AI-assistant-specific operating behavior
5. Relevant project documentation under `docs/`
6. Existing code and repository conventions

If instructions conflict, follow the higher-priority source and surface the conflict. Do not silently invent a compromise.

## Project identity and purpose
- Hackathon: AAVISHKARA-26.
- Problem: JP-012 — Customer Arrival Queue Simulation & Resource Allocation Optimizer.
- Domain: bank branch operations.
- Product: an explainable decision-support dashboard for a branch operations manager.
- Purpose: use synthetic customer-demand data to forecast demand, simulate multiple queues, evaluate staffing, compare a basic allocation with an optimized feasible allocation, explain the recommendation, and support what-if analysis.
- Required implementation language: Python for backend, simulation, optimization, and data work.
- Preferred backend: FastAPI.
- Frontend must use the repository's chosen web stack unless a human explicitly approves a change for a concrete requirement.

## Agent boundary
- Coding agents are implementation assistants, not project orchestrators.
- Do not infer that you are Kiran, Karthi, Reethu, or Deepansha.
- Do not infer ownership, authority, or teammate assignments from names, roles, or context files.
- Do not assign work to teammates or make claims about what another teammate is doing.
- `.chatgpt/` contains ChatGPT-only orchestration state. It is not a source of coding requirements or agent instructions.
- Do not autonomously implement the entire product when the user has requested an audit, plan, or scoped task.

## Competition timing and new-project rule
- Official event: 9 September 2026 10:00 AM through 10 September 2026 2:00 PM.
- Substantive development begins at 9 September 2026 1:30 PM.
- Before 1:30 PM, preparation such as repository inspection, environment setup, documentation reading, planning, and dependency preparation is permitted; do not implement the substantive JP-012 solution.
- The submitted judging version freezes at 10 September 2026 7:00 AM.
- After the 7:00 AM freeze, do not make team-initiated changes to source, repository contents, PPT, deployment, or judging materials unless an organizer authorizes an exceptional intervention.
- The submitted solution must be genuinely developed during the competition. Do not import or substantially reuse a completed pre-existing queue simulator, optimizer, dashboard, or other solution.
- Normal framework starters, open-source libraries, and standard developer tooling are permitted, subject to licenses and event rules.

## AI and collaboration integrity
- AI-assisted development is permitted by the event rules.
- Internet research, GitHub, legitimate external APIs/cloud services, and open-source libraries are permitted subject to the official rules.
- Only registered team members may provide technical contributions to the project. Do not solicit, simulate, or conceal technical work by unregistered people or other teams.
- AI-generated code must be understood, reviewed, exercised, and accepted by the registered team member responsible for the work before merge.
- AI usage must be disclosed in the event-required format. Maintain an accurate record of tool/service, team member using it, purpose, and brief description.
- Never misrepresent AI-generated or third-party work as human-original work.
- Do not fabricate test results, benchmark numbers, waiting-time improvements, citations, sources, or capabilities.

## Before editing
1. Inspect the relevant repository files and current implementation.
2. Read applicable `docs/` guidance and preserve established interfaces.
3. Check the current branch and recent repository changes when shared work may have changed.
4. Identify the smallest end-to-end change that satisfies the task.
5. Check whether another implementation already provides the requested behavior.
6. Identify file ownership and avoid editing another teammate's module without coordination.

## Engineering rules
- Prefer the smallest correct implementation over speculative architecture.
- Keep frontend, backend/API, simulation/optimization, data, AI helpers, and tests separated by responsibility.
- Avoid microservices, authentication, infrastructure work, or new frameworks unless explicitly required.
- Avoid unnecessary dependencies; prefer the Python standard library where practical.
- Never commit secrets, credentials, tokens, or real customer data.
- Use synthetic/self-created data for the hackathon MVP unless the official rules and project requirements explicitly permit something else.
- Validate external/user inputs at system boundaries.
- Handle expected failure cases with useful errors.
- Keep deterministic core business logic independent of LLMs or external AI services.
- Do not make an LLM the source of truth for forecasts, queue metrics, constraints, allocation decisions, or measured outcomes.
- Recommendations must remain explainable: expose important inputs, hard constraints, score/metric changes, and the reason for the selected allocation.
- Do not duplicate functionality or create parallel implementations without a concrete reason.
- Preserve working behavior and stable API contracts unless the task explicitly changes them.
- Make focused changes; do not reformat or rewrite unrelated files.

## P0 scope
The P0 judging path is:
`data → demand forecast → queue simulation → resource allocation → baseline comparison → explainable recommendation → what-if result`.

P0 must demonstrate:
- multiple service queues
- synthetic arrival/service data
- normal/peak/surge scenarios
- demand prediction by time slot
- waiting-time estimation
- feasible resource allocation under hard limits
- a basic allocation baseline
- measurable baseline vs optimized comparison
- overload detection
- explainable recommendation
- interactive what-if behavior

Do not start P1 work until P0 exit criteria are met.

## Simulation and optimization integrity
- Hard resource constraints are mandatory and must be enforced independently of objective scoring.
- Baseline and optimized runs must use comparable scenario inputs and simulation conditions.
- Optimizer correctness must be validated against the real simulation engine, not permanent mocks/stubs.
- Metrics must have explicit definitions and units.
- Any benchmark or improvement claim must come from actual execution.
- Deterministic seeded scenarios are preferred for reproducible demos and tests.

## Testing and verification
- Add focused tests for non-trivial simulation, forecasting, scoring, optimization, API, and integration logic as applicable.
- At minimum, test normal, peak, and surge behavior where those paths are affected.
- Test hard resource constraints and infeasible/invalid inputs.
- Test baseline vs optimized behavior using the same inputs.
- Run the narrowest relevant tests first, then the broader test suite when practical.
- Do not claim a feature works unless it was actually exercised or tested.
- If execution is unavailable, state that verification was not performed rather than inferring success.
- Report important assumptions and verification limits in the final handoff.

## Integration discipline
- Assume registered teammates may change the repository concurrently.
- Before editing a shared file, fetch/re-read its current contents; do not overwrite newer work from memory.
- Keep commits small and single-purpose.
- When an interface changes, update its direct consumers and focused tests in the same change when feasible.
- If a requested change conflicts with newer repository work, stop and surface the conflict instead of overwriting it.
- After meaningful changes, leave the repository in a runnable, testable state.

## Git discipline
- Keep `main` demoable.
- Prefer one short-lived feature branch per coherent task: `<task-id>-<short-description>`.
- Include the task ID in commits.
- Do not force-push or rewrite shared history unless a human explicitly directs it.
- Pull/re-read current `main` before starting work that depends on shared interfaces.

## Handoff format
Every meaningful implementation handoff should state:
1. What changed.
2. What was tested and the exact verification performed.
3. Any API/data/schema contract changes.
4. Dependencies for other modules.
5. Known risks or limitations.
6. Recommended next step.

Never end a handoff with an unsupported claim such as "everything is done".
