# AI Coding Instructions

These instructions apply to AI coding assistants working in this repository. They complement `AGENTS.md`; when there is a conflict, `AGENTS.md` and the user's explicit task take priority.

## Operating mode
- Inspect before editing: repository structure, relevant source files, docs, tests, and existing interfaces.
- Prefer the smallest working vertical slice.
- Reuse existing code before introducing abstractions or dependencies.
- Do not change frameworks or architecture without a concrete requirement.
- Never assume a file is unchanged because it was unchanged in an earlier conversation; re-read shared files before overwriting them.

## Product constraints
The project implements JP-012: bank-branch customer arrival queue simulation and resource allocation optimization.
The core decision loop is:
`data → demand forecast → queue simulation → allocation optimization → baseline comparison → explainable recommendation → what-if result`.

The deterministic simulation/optimization layer is authoritative. LLMs or other AI services may assist with explanation or optional UX, but must not be required for core correctness or become the source of operational decisions.

## Coding standards
- Keep modules cohesive and interfaces explicit.
- Validate all user/API inputs at boundaries.
- Handle expected errors with useful messages.
- Avoid unnecessary dependencies and duplicate implementations.
- Keep frontend/API, simulation/optimization, data generation, and tests separated.
- Never hard-code secrets, credentials, tokens, or real customer data.
- Preserve existing behavior unless the task explicitly changes it.
- Do not modify unrelated files.
- Keep configuration externalized where configuration is genuinely needed.

## Optimization/simulation standards
- Respect hard resource constraints.
- Keep recommendation logic explainable.
- Prefer transparent scoring/constraint logic over opaque optimization for hackathon MVP behavior.
- Make units and metric definitions explicit.
- Ensure baseline and optimized runs use comparable inputs and simulation conditions.
- Avoid claiming predictive or optimization performance without measured evidence.

## Testing
For non-trivial changes, add or update focused tests. Prioritize:
- queue behavior and waiting-time calculations
- normal/peak/surge scenarios
- hard resource constraints
- invalid/infeasible inputs
- baseline vs optimized comparison
- API contract behavior when applicable

Run focused tests first and broader checks when practical. Never report tests as passing unless they were actually run.

## Change discipline
- Make one coherent change at a time.
- Keep commits focused and easy to review.
- If another teammate's newer work is present, preserve it rather than replacing it from stale context.
- If an interface changes, update direct consumers and tests in the same change when feasible.
- At handoff, state what changed, what was tested, and any known limitation or assumption.

## Hackathon integrity
AI assistance is allowed by the event rules, but registered team members must understand and validate the generated implementation. Do not fabricate benchmark data, test results, sources, or capabilities.
