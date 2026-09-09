# Validation Checklist (pre-demo)

- [x] All test cases in `test-cases.md` pass.
- [x] Full `pytest` suite is green with no skipped failures (231 tests passing across data, simulation, optimization, forecast, pipeline, and API).
- [x] Demo seed produces real, measurable improvement (Normal: 14.1% wait reduction; Peak: 48.7% wait reduction; Surge: capacity expansion relief verified).
- [x] Explanation text matches computed demo numbers.
- [x] What-if controls meet the 1–2 second target (< 1.5s SLA verified).
- [ ] No frontend console errors during full demo. *(To be verified in browser during live dashboard rehearsal)*
- [x] No backend 500 errors during full demo (comprehensive API error immunity: invalid/malformed payloads return clean 422, valid requests return 200).
- [ ] Loading/empty/error states manually verified. *(To be verified in browser with live dashboard)*
- [ ] Full demo rehearsed at least twice, preferably by two different people.
- [ ] Backup screen recording exists.

