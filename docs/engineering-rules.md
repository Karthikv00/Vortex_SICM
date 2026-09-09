# Engineering Rules

These are team engineering workflow rules. Official AAVISHKARA-26 rules and the JP-012 problem statement have higher authority.

## Source of truth

- Official event rules/problem statement override project preferences.
- `AGENTS.md` defines repository-level coding-agent guardrails.
- `AI_INSTRUCTIONS.md` defines AI coding-assistant behavior.
- `docs/` contains the approved product/architecture/execution specifications.
- The current repository implementation is the source of truth for what is actually implemented, not for what the requirements mean.

## Competition integrity

- Substantive JP-012 development begins at **1:30 PM on 9 Sep 2026**.
- The final judging version freezes at **7:00 AM on 10 Sep 2026**.
- The submitted state is the judging baseline; do not make team-initiated modifications after the freeze unless organizers authorize an exception.
- The submitted solution must be genuinely developed during the competition; do not import or substantially reuse a completed pre-existing solution.
- Only registered team members may technically contribute.
- AI-assisted development is allowed, but the responsible registered team member must understand, validate, and test AI-generated code before merge.
- Maintain the required AI disclosure information: tool/service, team member, purpose, and brief description.
- Do not fabricate results, benchmark numbers, test outcomes, or improvement metrics.
- Use synthetic/self-created data for the MVP; never commit real customer data or secrets.

## Development workflow

- `architecture/api-contract.md` and `architecture/data-model.md` are binding contracts.
- New dependencies require justification; avoid duplicates and unnecessary infrastructure.
- `main` should remain demoable.
- Use one short-lived feature branch per task: `<task-id>-<short-description>`.
- Keep commits small and task-scoped; include task ID in commit messages.
- Pull/re-read current `main` before work that depends on shared interfaces.
- Before changing a shared file, inspect its current contents and diff; never overwrite newer teammate work from memory.
- Tests must pass locally before merge; never claim tests passed without execution.
- If execution is unavailable, explicitly record that verification was not performed.
- Contract changes must be announced in the agreed team coordination channel and documented in the same PR.
- Slack is the event stream, not the durable record; decisions belong in `docs/decisions/` or the relevant specification.

## Product engineering

- P0 comes before P1.
- P0 is: `data → demand forecast → queue simulation → resource allocation → baseline comparison → explainable recommendation → what-if result`.
- Deterministic simulation and optimization are authoritative.
- Hard resource constraints must never be overridden by AI-generated recommendations.
- Baseline and optimized comparisons must use comparable inputs and actual simulation results.
- Recommendations must expose meaningful inputs, constraints, score/metric changes, and reasons.
- Avoid authentication/RBAC, complex microservices, real bank integrations, unnecessary cloud infrastructure, deep-learning-heavy forecasting, and autonomous operational agents until P0 is stable and a concrete requirement exists.

## Coordination channels

- `#hackathon-command`: architecture, blockers, phase status, integration events.
- `#hackathon-backend`: backend/simulation/API.
- `#hackathon-frontend`: dashboard/UI.
- `#hackathon-qa`: testing/validation/demo.
- `#hackathon-decisions`: ADRs and scope changes.
