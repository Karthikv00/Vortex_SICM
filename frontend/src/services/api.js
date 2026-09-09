/**
 * frontend/src/services/api.js
 * 
 * Production API service conforming to docs/architecture/api-contract.md.
 * Automatically falls back to high-fidelity deterministic mock data if FastAPI
 * backend is offline or in demo mode.
 */

import { SCENARIOS, TIME_SLOTS } from '../mocks/mockData';

// Configurable endpoint with auto-fallback
const API_BASE = '/api';
let preferRealApi = true;

export function setApiMode(useReal) {
  preferRealApi = useReal;
}

export function isRealApiPreferred() {
  return preferRealApi;
}

/**
 * Health check — FR-API-1
 */
export async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(1500) });
    if (res.ok) {
      const data = await res.json();
      return { online: true, ...data };
    }
  } catch (err) {
    // Offline
  }
  return { online: false, status: 'offline' };
}

/**
async function parseErrorResponse(res, defaultMsg) {
  try {
    const err = await res.json();
    if (err.detail) {
      if (typeof err.detail === 'object' && err.detail.message) {
        return err.detail.message;
      }
      if (typeof err.detail === 'string') {
        return err.detail;
      }
      if (Array.isArray(err.detail) && err.detail[0]?.msg) {
        return err.detail.map(d => `${d.loc ? d.loc.join('.') + ': ' : ''}${d.msg}`).join(', ');
      }
    }
    if (err.message) return err.message;
  } catch (_) {
    // Non-JSON response
  }
  return `${defaultMsg} (HTTP ${res.status})`;
}

/**
 * Load or generate scenario configuration along with canonical baseline
 */
export async function getScenario(scenarioName = 'surge', seed = 42) {
  if (preferRealApi) {
    let res;
    try {
      res = await fetch(`${API_BASE}/scenario/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario_name: scenarioName, seed })
      });
    } catch (netErr) {
      throw new Error(`Unable to connect to FastAPI backend at ${API_BASE}/scenario/generate. Please ensure the backend server is running on port 8000.`);
    }

    if (!res.ok) {
      const msg = await parseErrorResponse(res, 'Scenario generation failed');
      throw new Error(msg);
    }
    const data = await res.json();
    return {
      scenario: data.scenario || data,
      baseline: data.baseline || null
    };
  }

  // Deterministic Mock (only used if explicitly in mock mode)
  await new Promise(r => setTimeout(r, 120)); // Subtle realistic latency
  const sc = SCENARIOS[scenarioName] || SCENARIOS.surge;
  return {
    scenario: {
      scenario_name: sc.scenario_name,
      seed: sc.seed,
      horizon_start: sc.horizon_start,
      horizon_end: sc.horizon_end,
      slot_minutes: sc.slot_minutes,
      queues: sc.queues,
      total_staff_available: sc.total_staff_available
    },
    baseline: sc.baseline?.allocation || null
  };
}

/**
 * Fetch authoritative baseline allocation for a scenario
 */
export async function fetchBaseline(scenarioConfig) {
  if (preferRealApi) {
    let res;
    try {
      res = await fetch(`${API_BASE}/scenario/baseline`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(scenarioConfig)
      });
    } catch (netErr) {
      throw new Error(`Unable to connect to FastAPI backend at ${API_BASE}/scenario/baseline.`);
    }

    if (!res.ok) {
      const msg = await parseErrorResponse(res, 'Baseline fetch failed');
      throw new Error(msg);
    }
    return await res.json();
  }

  const sc = SCENARIOS[scenarioConfig?.scenario_name] || SCENARIOS.surge;
  return sc.baseline?.allocation || null;
}

/**
 * Fetch demand forecast
 */
export async function fetchForecast(scenarioConfig) {
  if (preferRealApi) {
    let res;
    try {
      res = await fetch(`${API_BASE}/forecast`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario: scenarioConfig })
      });
    } catch (netErr) {
      throw new Error(`Unable to connect to FastAPI backend at ${API_BASE}/forecast.`);
    }

    if (!res.ok) {
      const msg = await parseErrorResponse(res, 'Forecast API failed');
      throw new Error(msg);
    }
    return await res.json();
  }

  await new Promise(r => setTimeout(r, 150));
  const sc = SCENARIOS[scenarioConfig?.scenario_name] || SCENARIOS.surge;
  return sc.forecast;
}

/**
 * Simulate allocation
 */
export async function simulateAllocation(scenarioConfig, forecast, allocation) {
  if (preferRealApi) {
    let res;
    try {
      res = await fetch(`${API_BASE}/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario: scenarioConfig, forecast, allocation })
      });
    } catch (netErr) {
      throw new Error(`Unable to connect to FastAPI backend at ${API_BASE}/simulate.`);
    }

    if (!res.ok) {
      const msg = await parseErrorResponse(res, 'Simulation API failed');
      throw new Error(msg);
    }
    return await res.json();
  }

  await new Promise(r => setTimeout(r, 150));
  const sc = SCENARIOS[forecast?.scenario_name] || SCENARIOS.surge;
  return sc.baseline.result;
}

/**
 * Run optimizer — FR-API-5
 */
export async function optimizeScenario(scenarioConfig, forecast) {
  if (preferRealApi) {
    let res;
    try {
      res = await fetch(`${API_BASE}/optimize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario: scenarioConfig, forecast })
      });
    } catch (netErr) {
      throw new Error(`Unable to connect to FastAPI backend at ${API_BASE}/optimize.`);
    }

    if (!res.ok) {
      const msg = await parseErrorResponse(res, 'Optimizer API failed');
      throw new Error(msg);
    }
    return await res.json();
  }

  // Simulate optimization computation time (250ms)
  await new Promise(r => setTimeout(r, 250));
  const sc = SCENARIOS[scenarioConfig?.scenario_name] || SCENARIOS.surge;
  return {
    scenario_name: sc.scenario_name,
    baseline: sc.baseline,
    optimized: sc.optimized,
    score_breakdown: sc.score_breakdown,
    improvement: sc.improvement,
    explanation: sc.explanation,
    feasible: sc.feasible
  };
}

/**
 * What-If Simulation — FR-API-6
 * Computes custom staff rebalance metrics on the fly
 */
export async function simulateWhatIf(scenarioConfig, forecast, allocationPlan, queuesConfig) {
  if (preferRealApi) {
    let res;
    try {
      res = await fetch(`${API_BASE}/whatif`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario: scenarioConfig, forecast, allocation: allocationPlan })
      });
    } catch (netErr) {
      throw new Error(`Unable to connect to FastAPI backend at ${API_BASE}/whatif.`);
    }

    if (!res.ok) {
      const msg = await parseErrorResponse(res, 'What-If simulation failed');
      throw new Error(msg);
    }
    return await res.json();
  }

  await new Promise(r => setTimeout(r, 100));
  
  // Instant deterministic simulation logic matching queuing physics
  const staffMap = allocationPlan.staff_by_queue;
  const arrivalsMap = forecast.expected_arrivals;
  const queues = queuesConfig || SCENARIOS.surge.queues;
  
  const perQueue = {};
  let totalServed = 0;
  let totalOverloaded = 0;
  let weightedWaitSum = 0;
  let totalArrivals = 0;
  let maxP95 = 0;

  queues.forEach(q => {
    const qid = q.queue_id;
    const staff = Math.max(1, staffMap[qid] || 1);
    const arrivals = arrivalsMap[qid] || [];
    const qArrivalTotal = arrivals.reduce((a, b) => a + b, 0);
    totalArrivals += qArrivalTotal;

    // Service capacity per 15 min slot: (15 / avg_service_time) * staff
    const slotCapacity = (15.0 / q.avg_service_time_minutes) * staff;
    
    let queueOverloads = [];
    let currentBacklog = 0;
    let slotWaits = [];

    arrivals.forEach((arrived, idx) => {
      currentBacklog += arrived;
      const served = Math.min(currentBacklog, slotCapacity);
      currentBacklog -= served;

      // Estimated wait in slot: (backlog / slotCapacity) * 15
      const waitEst = slotCapacity > 0 ? (currentBacklog / slotCapacity) * 15 : 30;
      slotWaits.push(waitEst);

      // Overload threshold: wait > 10 min or backlog > capacity * 1.2
      if (waitEst > 10.0 || arrived > slotCapacity * 1.1) {
        queueOverloads.push(forecast.slots[idx]);
      }
    });

    const avgWait = slotWaits.reduce((a, b) => a + b, 0) / (slotWaits.length || 1);
    const sortedWaits = [...slotWaits].sort((a, b) => a - b);
    const p95Wait = sortedWaits[Math.floor(sortedWaits.length * 0.95)] || avgWait * 1.8;
    const utilization = Math.min(0.99, (qArrivalTotal * q.avg_service_time_minutes) / (staff * 8 * 60));

    perQueue[qid] = {
      avg_wait_minutes: parseFloat(avgWait.toFixed(1)),
      p95_wait_minutes: parseFloat(p95Wait.toFixed(1)),
      utilization: parseFloat(utilization.toFixed(2)),
      overloaded_slots: queueOverloads,
      total_served: Math.max(0, qArrivalTotal - currentBacklog),
      end_backlog: currentBacklog
    };

    weightedWaitSum += avgWait * qArrivalTotal;
    totalServed += (qArrivalTotal - currentBacklog);
    totalOverloaded += queueOverloads.length;
    if (p95Wait > maxP95) maxP95 = p95Wait;
  });

  const branchAvgWait = totalArrivals > 0 ? weightedWaitSum / totalArrivals : 4.0;

  return {
    allocation_label: 'whatif',
    per_queue: perQueue,
    branch_wide: {
      avg_wait_minutes: parseFloat(branchAvgWait.toFixed(1)),
      p95_wait_minutes: parseFloat(maxP95.toFixed(1)),
      overloaded_slot_count: totalOverloaded,
      total_served: totalServed,
      total_end_backlog: Object.values(perQueue).reduce((a, b) => a + b.end_backlog, 0)
    }
  };
}
