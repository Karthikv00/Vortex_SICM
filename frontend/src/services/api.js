/**
 * frontend/src/services/api.js
 *
 * Production API service conforming to docs/architecture/api-contract.md.
 * Mock data is available only when explicitly switched to mock mode.
 */

import { SCENARIOS } from '../mocks/mockData';

const API_BASE = '/api';
let preferRealApi = true;

export function setApiMode(useReal) {
  preferRealApi = useReal;
}

export function isRealApiPreferred() {
  return preferRealApi;
}

async function parseApiError(res, fallback) {
  const err = await res.json().catch(() => ({}));
  return err?.detail?.message || err?.message || fallback;
}

export async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(1500) });
    if (res.ok) {
      const data = await res.json();
      return { online: true, ...data };
    }
  } catch (err) {
    // Backend unavailable.
  }
  return { online: false, status: 'offline' };
}

export async function getScenario(scenarioName = 'surge', seed = 42) {
  if (preferRealApi) {
    const res = await fetch(`${API_BASE}/scenario/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scenario_name: scenarioName, seed }),
    });
    if (!res.ok) {
      throw new Error(await parseApiError(res, `Scenario generation failed with status ${res.status}`));
    }
    const data = await res.json();
    return { scenario: data.scenario || data, baseline: data.baseline || null };
  }

  await new Promise(r => setTimeout(r, 120));
  const sc = SCENARIOS[scenarioName] || SCENARIOS.surge;
  return {
    scenario: {
      scenario_name: sc.scenario_name,
      seed: sc.seed,
      horizon_start: sc.horizon_start,
      horizon_end: sc.horizon_end,
      slot_minutes: sc.slot_minutes,
      queues: sc.queues,
      total_staff_available: sc.total_staff_available,
    },
    baseline: sc.baseline?.allocation || null,
  };
}

export async function fetchBaseline(scenarioConfig) {
  if (preferRealApi) {
    const res = await fetch(`${API_BASE}/scenario/baseline`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(scenarioConfig),
    });
    if (!res.ok) {
      throw new Error(await parseApiError(res, `Baseline API failed with status ${res.status}`));
    }
    return await res.json();
  }

  const sc = SCENARIOS[scenarioConfig?.scenario_name] || SCENARIOS.surge;
  return sc.baseline?.allocation || null;
}

export async function fetchForecast(scenarioConfig) {
  if (preferRealApi) {
    const res = await fetch(`${API_BASE}/forecast`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scenario: scenarioConfig }),
    });
    if (!res.ok) {
      throw new Error(await parseApiError(res, `Forecast API failed with status ${res.status}`));
    }
    return await res.json();
  }

  await new Promise(r => setTimeout(r, 150));
  const sc = SCENARIOS[scenarioConfig?.scenario_name] || SCENARIOS.surge;
  return sc.forecast;
}

export async function simulateAllocation(scenarioConfig, forecast, allocation) {
  if (preferRealApi) {
    const res = await fetch(`${API_BASE}/simulate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scenario: scenarioConfig, forecast, allocation }),
    });
    if (!res.ok) {
      throw new Error(await parseApiError(res, `Simulation API failed with status ${res.status}`));
    }
    return await res.json();
  }

  await new Promise(r => setTimeout(r, 150));
  const sc = SCENARIOS[forecast?.scenario_name] || SCENARIOS.surge;
  return sc.baseline.result;
}

export async function optimizeScenario(scenarioConfig, forecast) {
  if (preferRealApi) {
    const res = await fetch(`${API_BASE}/optimize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scenario: scenarioConfig, forecast }),
    });
    if (!res.ok) {
      throw new Error(await parseApiError(res, `Optimizer API failed with status ${res.status}`));
    }
    return await res.json();
  }

  await new Promise(r => setTimeout(r, 250));
  const sc = SCENARIOS[scenarioConfig?.scenario_name] || SCENARIOS.surge;
  return {
    scenario_name: sc.scenario_name,
    baseline: sc.baseline,
    optimized: sc.optimized,
    score_breakdown: sc.score_breakdown,
    improvement: sc.improvement,
    explanation: sc.explanation,
    feasible: sc.feasible,
  };
}

export async function simulateWhatIf(scenarioConfig, forecast, allocationPlan) {
  if (preferRealApi) {
    const res = await fetch(`${API_BASE}/whatif`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scenario: scenarioConfig, forecast, allocation: allocationPlan }),
    });
    if (!res.ok) {
      throw new Error(await parseApiError(res, `What-If simulation failed with status ${res.status}`));
    }
    return await res.json();
  }

  const sc = SCENARIOS[scenarioConfig?.scenario_name] || SCENARIOS.surge;
  return sc.what_if?.[JSON.stringify(allocationPlan.staff_by_queue)] || sc.baseline.result;
}
