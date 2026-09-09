# Engineering Rules

- `architecture/api-contract.md` and `architecture/data-model.md` are binding contracts.
- New dependencies require justification; avoid duplicates and unnecessary infrastructure.
- `main` should remain demoable. Use one short-lived feature branch per task: `<task-id>-<short-description>`.
- Keep commits small and task-scoped; include task ID in commit messages.
- Tests must pass locally before merge; never claim tests passed without execution.
- No secrets, credentials, tokens, or real customer data.
- AI-generated code must be understood and validated by registered team members before merge.
- P1 features do not start before P0 exit criteria are met.
- If a shared file changed, inspect the current diff and preserve compatible teammate work; never blindly overwrite.
- Contract changes must be announced in `#hackathon-command` and documented in the same PR.
- Slack is the event stream, not the durable record; decisions belong in `docs/decisions/` or relevant docs.

## Coordination channels
- `#hackathon-command`: architecture, blockers, phase status, integration events.
- `#hackathon-backend`: backend/simulation/API.
- `#hackathon-frontend`: dashboard/UI.
- `#hackathon-qa`: testing/validation/demo.
- `#hackathon-decisions`: ADRs and scope changes.
