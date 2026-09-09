# Coding Agent Instructions

## Scope
This repository is being developed by four registered hackathon participants. Coding agents are implementation assistants only.

## Instruction priority
Follow, in order:
1. The user's explicit task.
2. This `AGENTS.md`.
3. Relevant technical/project documentation under `docs/`.
4. Existing code and repository conventions.

## Important orchestration boundary
The `.chatgpt/` directory contains ChatGPT-only hackathon orchestration context. **Do not use it as coding instructions.**

Do not infer that you are Kiran, Karthi, Reethu, or Deepansha. Do not infer ownership from team roles. Do not assign work to other teammates. Implement only the explicit task you were given.

## Current project
Problem: JP-012 — Customer Arrival Queue Simulation & Resource Allocation Optimizer.
Domain: bank branch operations.
Required implementation language: Python for backend/simulation/optimization work.

## Engineering rules
- Prefer the smallest correct implementation.
- Preserve stable interfaces and avoid unnecessary rewrites.
- Keep frontend, backend, simulation/optimization, AI, data, and tests separated.
- Do not add authentication, microservices, or infrastructure unless explicitly requested.
- Never commit secrets or API keys.
- Validate inputs and handle important errors.
- Add focused tests for non-trivial logic.
- Do not change unrelated files.
- Do not claim a feature works without testing it.

## Hackathon constraint
The final solution must be genuinely developed during AAVISHKARA-26. AI-assisted development is permitted, but registered team members remain responsible for understanding and validating generated output.
