# Vortex SICM Documentation

This directory contains the project's requirements, architecture, design, execution, testing, and decision records.

## Start here

- `requirements/` — PRD, functional/non-functional requirements, acceptance criteria
- `architecture/` — system architecture, domain/data models, simulation and optimization design, API contract, TRD
- `design/` — UX, dashboard specification, demo flow
- `execution/` — phases, task board, dependencies, integration plan, project status, submission checklist
- `testing/` — test strategy, test cases, validation checklist
- `decisions/` — architecture and scope decision records
- `team/` — team execution documents
- `risk-register.md` — known risks and mitigations
- `engineering-rules.md` — engineering workflow and repository guardrails
- `demo-script.md` — concise demonstration flow
- `release-audit.md` — release/readiness audit

## Authority model

1. Official AAVISHKARA-26 rules and JP-012 problem statement
2. Explicit human team instructions
3. `AGENTS.md` and `AI_INSTRUCTIONS.md` for repository/AI behavior
4. Approved specifications in this directory
5. ADRs and engineering inference
6. Current source code and tests determine what is actually implemented

Documentation describes intended behavior; the running code and test results determine implementation status. Do not mark functionality complete solely because a file or endpoint exists.

## Core product flow

`custom/built-in scenario → forecast → multi-queue simulation → baseline allocation → constrained optimization → comparison → explanation → what-if/stress test`

The product is a decision-support system for branch operations. The deterministic simulation and optimization layer remains the source of truth; AI-assisted development does not make the product an autonomous banking agent.