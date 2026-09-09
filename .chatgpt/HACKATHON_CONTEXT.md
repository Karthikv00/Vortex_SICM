# ⚠️ CHATGPT-ONLY HACKATHON ORCHESTRATION CONTEXT

> **This file is exclusively for ChatGPT orchestration.** It is not project requirements, architecture, or coding instructions.
>
> Coding agents MUST NOT infer developer identity, ownership, task assignments, or implementation requirements from this file. They must follow the user's explicit task, `AGENTS.md`, and relevant project documentation.
>
> ChatGPT acts as the team's orchestration/CTO layer: maintain state, decompose work, allocate tasks, manage dependencies, challenge scope, track risks, and coordinate the four registered members.

## Event
- AAVISHKARA-26, 24-hour hackathon.
- Official event: 9 Sep 2026 10:00 AM → 10 Sep 2026 2:00 PM.
- Development begins: 9 Sep 2026 1:30 PM.
- Final submission freeze: 10 Sep 2026 7:00 AM; submitted version is the judging baseline.
- Break: 7:00–8:00 AM; breakfast 8:00–9:00 AM.
- Presentation: 9:00 AM–12:30 PM; target slot ~10–12 min = 5 min PPT + 3 min demo + 2 min Q&A, plus setup/transition.
- Final evaluation: 1:00–2:30 PM.
- AI-assisted development, internet, external APIs, cloud services, GitHub, and open-source libraries are permitted; AI usage must be disclosed. Only registered team members may contribute technical work.

## Team
- Kiran — core member; primary AI/optimization/product lead; also helps backend.
- Karthi — core member; primary backend/simulation lead; Kiran assists.
- Deepansha — beginner; simpler UI/frontend tasks.
- Reethu — beginner; simpler QA/data/demo-validation tasks.
- All four work simultaneously on the same repository and each has a laptop.
- Assume all members are beginner-level vibe coders; tasks must be explicit and independently verifiable.

## Chosen problem
**JP-012 — Customer Arrival Queue Simulation & Resource Allocation Optimizer**.
Domain: **bank branch operations**.

Core requirements from the problem statement:
- Analyze customer arrival patterns, appointment schedules, and available resources.
- Simulate multiple service queues.
- Estimate waiting time.
- Predict demand by time slot.
- Recommend staff/resource allocation.
- Identify overloaded periods.
- Compare optimized allocation with a basic allocation strategy.
- Respect resource limits.
- Recommendation logic must be explainable.

## Product direction
Build an **AI-assisted bank operations decision-support system**, not merely a queue simulator.

Core loop:
`Historical/synthetic data → demand forecast → queue simulation → multi-objective resource optimization → explainable recommendation → what-if simulation → before/after comparison.`

Primary user: bank branch operations manager.

MVP scenarios: normal day, peak period, sudden surge.

Primary demo outcome: **prove that an allocation decision reduces waiting time under resource constraints.**

Demo story:
1. Show current branch state.
2. Trigger peak/surge demand.
3. Detect projected overload.
4. Recommend a resource reallocation with reasons.
5. Simulate the recommendation.
6. Compare baseline vs optimized results.
7. Show measurable improvement and explain why.

## Technical decisions / defaults
- Python is mandatory.
- Preferred backend: FastAPI.
- Preferred frontend: Next.js + TypeScript + Tailwind unless existing repo constraints justify otherwise.
- Use deterministic/stochastic queue simulation and optimization as the source of truth.
- AI approach: hybrid. Use a simple explainable forecasting model; optimization should be mathematical/constraint-based; LLM is optional for natural-language explanations/scenario assistance, not the sole decision engine.
- Multi-objective optimization: prioritize reduced waiting time, while balancing overload/queue performance and staff utilization subject to hard resource constraints.
- Keep staff skills and complex appointment modeling out of the initial MVP unless they become necessary for differentiation.
- Keep persistence/authentication optional. Prefer no database for MVP unless saved scenarios/history materially improve the demo.
- Generate synthetic bank customer data; no organizer dataset is available.
- Keep CSV upload out of MVP unless needed.

## Scope discipline
### P0 / must work
- Bank branch with multiple service queues.
- Synthetic customer arrival/service data.
- Normal/peak/surge scenarios.
- Queue simulation.
- Waiting-time metrics.
- Demand forecast.
- Resource constraints.
- Multi-objective allocation recommendation.
- Baseline vs optimized comparison.
- Explainable recommendation.
- Interactive what-if simulation.
- Strong operations dashboard.

### P1 / only if P0 is stable
- User-adjustable parameters.
- Scenario save/share.
- More detailed appointment handling.
- Staff skill compatibility.
- CSV import.

### Explicitly avoid unless everything else is finished
- Authentication.
- Complex microservices.
- Real bank integrations.
- Large-scale cloud infrastructure.
- Sophisticated deep learning.
- Autonomous AI agents controlling operations.

## Repository state at planning start
Repository: `Kiran-official/Vortex_SICM`, default branch `main`.
It is currently a universal hackathon boilerplate with empty starter directories and planning docs. Existing top-level structure includes:
- `.chatgpt/`
- `ai/`
- `assets/`
- `backend/`
- `data/`
- `database/`
- `docs/`
- `frontend/`
- `infra/`
- `scripts/`
- `tests/`
- `AI_INSTRUCTIONS.md`
- `README.md`

Existing `AI_INSTRUCTIONS.md` gives general coding guidance; it must not override explicit task instructions or this orchestration boundary.

## Orchestration rules
- ChatGPT owns overall decomposition and prioritization; members own implementation decisions within assigned areas.
- Give beginners bounded tasks with explicit inputs/outputs and acceptance criteria.
- Keep interfaces stable so four people can work in parallel.
- Prefer vertical, testable slices over disconnected scaffolding.
- Do not let one person's work block all others unnecessarily.
- Merge/integrate frequently and verify end-to-end after major milestones.
- No coding agent should infer that it is Kiran/Karthi/Reethu/Deepansha.
- Coding agents execute explicit implementation tasks only; they do not orchestrate teammates.

## Decision target
The judges should remember:
**B + C + E — the optimizer measurably reduces waiting time, the what-if simulation makes the decision tangible, and the recommendation is explainable.**
