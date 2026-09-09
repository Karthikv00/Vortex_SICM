# ADR-004: Optimization Strategy

**Status:** Accepted; sizing to be confirmed with real implementation measurements during KIRAN-001.

## Decision
Use exhaustive enumeration of feasible allocations, scored by the weighted objective in `architecture/optimization-design.md`. Do not add scipy.optimize, OR-Tools, or metaheuristics for P0.

## Sizing
At ≤6 queues and ≤20 staff, bounded staff compositions are low hundreds to low thousands before constraint filtering. With a simulation target under 1 second and optimize target under 3 seconds, enumeration is the simplest deterministic approach, but the real implementation must be benchmarked.

## Rationale
Enumeration is deterministic, easy to debug, and easy to explain: check every valid allocation and choose the best score. More sophisticated solvers add dependencies and abstraction without demonstrated need at this scale.

## Consequence
This does not scale to very large branch networks. Revisit only if future requirements materially exceed hackathon scope.
