# Non-Functional Requirements

## Performance
- Single simulation run: under 1 second on a standard laptop.
- Full enumeration + scoring optimization: under 3 seconds for ≤6 queues and ≤20 total staff.
- What-if dashboard interaction: 1–2 seconds.

## Reliability
- Simulation and optimization deterministic for the same seed and inputs.
- API returns structured errors, never raw stack traces.
- Edge cases such as zero arrivals, zero staff, and impossible allocation must not crash the system.

## Usability
- Dashboard communicates overload → recommendation → improvement within seconds.
- Explanation panel uses plain language.

## Maintainability
- Simulation, forecasting, and optimization independently testable without API/UI.
- No duplicate implementations.
- Configuration lives in one place, not scattered as magic numbers.

## Security
- No secrets, credentials, or real customer data in the repository.
- Validate API inputs at the boundary.

## Portability
- Local standard Python environment; `pip install -r requirements.txt` and `uvicorn` are sufficient.
- Docker optional, not required for the demo.

## Accessibility
- Readable contrast and legible font sizes at hackathon-demo baseline.
