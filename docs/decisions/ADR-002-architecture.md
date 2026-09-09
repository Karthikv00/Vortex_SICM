# ADR-002: Architecture Style

**Status:** Accepted

## Decision
Use a modular monolith: one FastAPI backend with separated internal modules for data, simulation, forecasting, optimization, and API, plus one frontend app. No network boundary between backend modules.

## Rationale
This gives most parallel-work benefits of microservices through stable internal contracts without deployment/network complexity. A single unstructured script would harm independent testability and parallel development.

## Consequences
`data-model.md` and `api-contract.md` must be treated as locked interfaces and changed deliberately.
