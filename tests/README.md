# Tests

Automated verification for Vortex SICM.

Run the full suite from the repository root:

```bash
pytest tests/ -v
```

Coverage includes API contracts, models, synthetic data, forecasting, simulation, optimization, persistence, custom workloads, stress testing, and end-to-end integration scenarios.

A feature is not considered verified because its implementation exists; use the test results and actual execution behavior as evidence.