# ADR-001: Project Scope

**Status:** Accepted

## Decision
Build an explainable decision-support loop: data → forecast → simulation → optimization → explanation → what-if → comparison, scoped to P0.

Explicitly exclude auth, microservices, real bank integrations, deep learning, reinforcement learning, autonomous agents, and complex infrastructure for the hackathon timeframe.

## Rationale
A bare simulator would miss the optimization/explainability value proposition. A production-style system would consume the limited hackathon time on infrastructure.

## Consequences
P1 features such as CSV import, persistence, and skill compatibility are deferred until P0 is stable.
