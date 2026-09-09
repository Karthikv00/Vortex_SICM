# ADR-003: Simulation Model

**Status:** Accepted

## Decision
Use fixed-width time-step simulation with default 15-minute slots and average service time per queue, rather than stochastic per-customer service times.

## Rationale
It is fast to build correctly, deterministic, explainable, and sufficient to demonstrate surge → overload → reallocation → improvement. Full discrete-event simulation adds complexity; purely analytical queueing theory fits time-varying demand less well.

## Consequence
Within-slot dynamics are approximated. This is a deliberate hackathon simplification.
