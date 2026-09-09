# Dependency Map

## Stable contracts
`architecture/data-model.md` unblocks KARTHI-002, DEEPANSHA-001, and REETHU-001. `architecture/api-contract.md` unblocks Deepansha's mock client and KARTHI-005.

## Real dependency chain
`KARTHI-001 → KARTHI-002 → KARTHI-003 → KIRAN-002 → KIRAN-003/KIRAN-004 → KARTHI-005 → DEEPANSHA-003/REETHU-003`.

`KARTHI-004` runs alongside KARTHI-003 after data/model dependencies are ready.

`DEEPANSHA-001 → DEEPANSHA-002 → DEEPANSHA-003` is independent of backend until final integration.

## Critical bottleneck
`KARTHI-003` is the critical-path backend item. Optimization correctness depends on a correct simulation engine.

## Important non-dependency
Frontend must not wait for backend. Mock-first development is intentional.
