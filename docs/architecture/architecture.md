# Architecture

## Style
Modular monolith: single FastAPI backend with clear internal modules and a single frontend app. No microservices.

## Logical flow

Data generation/input → data processing → demand prediction → queue simulation → baseline evaluation → resource optimizer → what-if simulation → metrics/comparison → explainable recommendation → FastAPI → dashboard.

## Module boundaries
| Module | Responsibility | Directory |
|---|---|---|
| Data | synthetic arrival/service generation, scenario profiles | `data/` |
| Simulation | time-step queue simulation, wait/utilization metrics | `backend/simulation/` |
| Forecasting | demand prediction | `backend/forecasting/` |
| Optimization | allocation enumeration, scoring, recommendation | `backend/optimization/` |
| API | FastAPI app and orchestration | `backend/` |
| UI | dashboard | `frontend/` |
| Tests | unit/integration/contract tests | `tests/` |

The simulation and optimization core must run and be testable with plain Python calls, without FastAPI, HTTP, or UI.

## Rationale
A modular monolith is simplest to run, debug, and demo live. Stable contracts let backend, simulation, optimization, QA, and frontend work in parallel without network/deployment complexity.

The deterministic simulation/optimization layer is the source of truth. Any LLM use is optional and outside the decision loop.

## Explicit non-goals
No auth, RBAC, microservices, real bank APIs, IoT, complex cloud infrastructure, deep learning, reinforcement learning, autonomous agents, overengineered databases, or required LLM dependency.
