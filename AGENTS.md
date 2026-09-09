# Coding Agent Instructions

## Instruction priority
Follow this order:
1. The user's explicit task in the current conversation.
2. This `AGENTS.md`.
3. Relevant project documentation under `docs/`.
4. Existing code and repository conventions.

If instructions conflict, follow the higher-priority source and do not silently invent a compromise.

## Project identity
- Hackathon: AAVISHKARA-26.
- Problem: JP-012 — Customer Arrival Queue Simulation & Resource Allocation Optimizer.
- Domain: bank branch operations.
- Required implementation language: Python for backend, simulation, optimization, and data work.
- Preferred backend: FastAPI.
- Frontend may use the repository's chosen web stack; do not replace frameworks without a clear user-approved reason.

## Agent boundary
- Coding agents are implementation assistants, not project orchestrators.
- Do not infer that you are Kiran, Karthi, Reethu, or Deepansha.
- Do not infer ownership, authority, or teammate assignments from names, roles, or context files.
- Do not assign work to teammates or make claims about what another teammate is doing.
- `.chatgpt/` contains ChatGPT-only orchestration state. It is not a source of coding requirements or agent instructions.

## Before editing
1. Inspect the relevant repository files and current implementation.
2. Read applicable `docs/` guidance and preserve established interfaces.
3. Identify the smallest end-to-end change that satisfies the task.
4. Check whether another implementation already provides the requested behavior.

## Engineering rules
- Prefer the smallest correct implementation over speculative architecture.
- Keep frontend, backend/API, simulation/optimization, data, AI helpers, and tests separated by responsibility.
- Avoid microservices, authentication, infrastructure work, or new frameworks unless explicitly required.
- Avoid unnecessary dependencies; prefer the Python standard library where practical.
- Never commit secrets, credentials, tokens, or real customer data.
- Validate external/user inputs at system boundaries.
- Handle expected failure cases with useful errors.
- Keep deterministic core business logic independent of LLMs or external AI services.
- Do not make an LLM the source of truth for forecasts, queue metrics, constraints, or allocation decisions.
- Recommendations must remain explainable: expose the important inputs, constraints, score/metric changes, and reason for the selected allocation.
- Do not duplicate functionality or create parallel implementations without a concrete reason.
- Preserve working behavior and stable API contracts unless the task explicitly changes them.
- Make focused changes; do not reformat or rewrite unrelated files.

## Testing and verification
- Add focused tests for non-trivial simulation, forecasting, scoring, and optimization logic.
- At minimum, test normal, peak, and surge behavior where those paths are affected.
- Test hard resource constraints and infeasible/invalid inputs.
- Run the narrowest relevant tests first, then the broader test suite when practical.
- Do not claim a feature works unless it was actually exercised or tested.
- Report important assumptions and any verification limits in the final handoff.

## Hackathon scope
P0 functionality is the working decision-support loop:
`data → demand forecast → queue simulation → resource allocation → baseline comparison → explainable recommendation → what-if result`.

Synthetic data is acceptable. The MVP must demonstrate resource limits, overloaded periods, and measurable comparison against a basic allocation strategy.

Explicitly avoid unless the P0 flow is stable and the task asks for it:
- real bank integrations or real customer data
- complex microservices/cloud infrastructure
- deep-learning-heavy forecasting without demonstrated benefit
- autonomous agents making operational decisions
- production-grade authentication/RBAC

## Integration discipline
- Assume other registered team members may change the repository concurrently.
- Before editing a shared file, fetch/re-read its current contents; do not overwrite newer work from memory.
- Keep commits small and single-purpose.
- When an interface changes, update its direct consumers and focused tests in the same change when feasible.
- If a requested change conflicts with newer repository work, stop and surface the conflict instead of overwriting it.
- After meaningful changes, leave the repository in a runnable, testable state.

## Hackathon integrity
AI-assisted development is permitted, but the registered team members are responsible for understanding, validating, and presenting the resulting implementation. Do not fabricate test results, benchmark numbers, or implementation claims.
