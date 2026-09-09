# Risk Register

| Risk | Probability | Impact | Mitigation | Owner |
|---|---|---|---|---|
| Simulation correctness / wait-time math | Medium | High | Edge-case tests and Reethu review before optimization | Karthi / Reethu |
| Infeasible optimizer allocation | Low–Medium | High | Filter hard constraints during enumeration; constraint tests | Kiran |
| Unrealistic synthetic surge | Medium | Medium | Demo realism check before lock | Reethu |
| Late frontend/backend integration failure | Medium | High | Mock-first frontend and early C4 checkpoint | Deepansha / Karthi |
| Scope explosion | Medium | High | P0 phase gating | Kiran |
| Dependency/environment conflicts | Low | Medium | Stdlib-first policy and shared requirements | Karthi |
| Insufficient testing time | Medium | High | Continuous testing from P1 | Reethu |
| Demo failure | Medium | High | Seeded demo, backup recording, two rehearsals | Reethu / Kiran |
| Stale AI context overwrites teammate work | Medium | Medium | Re-read current repo/context before edits | All |
| Merge conflicts | Medium | Low–Medium | Small feature branches/commits | All |
| Optimization exceeds 3s | Low | Medium | Real benchmark in KIRAN-001 | Kiran |
| Judges do not understand explanation | Medium | Medium | First-class explanation panel tied to real numbers | Kiran / Deepansha |
| No measurable improvement | Low–Medium | High | Honest baseline + realism validation | Reethu / Kiran |
