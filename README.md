# Universal Hackathon Boilerplate

A technology-agnostic starter workspace for rapid hackathon development.

## Philosophy
- Keep the base stack neutral.
- Choose technologies after the case study is revealed.
- Use AI tools to accelerate implementation, not to replace architecture decisions.
- Keep secrets out of Git.
- Keep frontend, backend, AI, data, docs, and tests separated.

## Suggested workflow
1. Read the case study.
2. Write requirements in `docs/requirements.md`.
3. Decide the minimum viable architecture in `docs/architecture.md`.
4. Generate/design UI with Stitch or another design tool.
5. Implement with the most suitable language/framework.
6. Add AI/model/API integration only where needed.
7. Run tests.
8. Containerize with Docker if useful.
9. Commit working milestones to Git.

## Folders
- `frontend/` — UI/client code
- `backend/` — server/API code
- `ai/` — prompts, model integration, ML/AI code
- `database/` — schema, migrations, seed data
- `data/` — local datasets/sample data (do not commit secrets or huge datasets)
- `assets/` — images, icons, design exports
- `docs/` — requirements, architecture, API notes
- `tests/` — tests
- `scripts/` — helper scripts
- `infra/` — Docker/deployment/infrastructure files

## Important
This is intentionally NOT tied to Python, Java, JavaScript, React, Node, etc. Add only what the case study actually requires.
