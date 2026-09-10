/**
 * frontend/src/services/api.js
 *
 * Production API service conforming to docs/architecture/api-contract.md.
 * Automatically falls back to high-fidelity deterministic mock data if FastAPI
 * backend is offline or in demo mode.
 */

import { SCENARIOS, TIME_SLOTS } from '../mocks/mockData';
import { normalizeTasksForApi } from '../utils/taskModel';

// Configurable endpoint with auto-fallback
const API_BASE = '/api';
let preferRealApi = true;

export function setApiMode(useReal) {
  preferRealApi = useReal;
}

export function isRealApiPreferred() {
  return preferRealApi;
}

/** Health check — FR-API-1 */
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

async function parseErrorResponse(res, defaultMsg) {
  try {
    const err = await res.json();
    if (err.detail) {
      if (typeof err.detail === 'object' && err.detail.message) return err.detail.message;
      if (typeof err.detail === 'string') return err.detail;
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

/** Load or generate scenario configuration along with canonical baseline */
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

    if (!res.ok) throw new Error(await parseErrorResponse(res, 'Scenario generation failed'));
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
      total_staff_available: sc.total_staff_available
    },
    baseline: sc.baseline?.allocation || null
  };
}

/** Fetch authoritative baseline allocation for a scenario */
export async function fetchBaseline(scenarioConfig) {
  if (preferRealApi) {
    let res;
    try {
      res = await fetch(`${API_BASE}/scenario/baseline`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(scenarioConfig)
      });
    } catch (netErr) {
      throw new Error(`Unable to connect to FastAPI backend at ${API_BASE}/scenario/baseline.`);
    }
    if (!res.ok) throw new Error(await parseErrorResponse(res, 'Baseline fetch failed'));
    return await res.json();
  }
  const sc = SCENARIOS[scenarioConfig?.scenario_name] || SCENARIOS.surge;
  return sc.baseline?.allocation || null;
}

/** Fetch demand forecast */
export async function fetchForecast(scenarioConfig) {
  if (preferRealApi) {
    let res;
    try {
      res = await fetch(`${API_BASE}/forecast`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ scenario: scenarioConfig })
      });
    } catch (netErr) {
      throw new Error(`Unable to connect to FastAPI backend at ${API_BASE}/forecast.`);
    }
    if (!res.ok) throw new Error(await parseErrorResponse(res, 'Forecast API failed'));
    return await res.json();
  }
  await new Promise(r => setTimeout(r, 150));
  const sc = SCENARIOS[scenarioConfig?.scenario_name] || SCENARIOS.surge;
  return sc.forecast;
}

/**
 * Analyze user-defined tasks. The backend automatically determines normal/peak/surge
 * from aggregate demand, builds the task-derived forecast, and runs resource optimization.
 */
export async function analyzeCustomWorkload(customTasks) {
  const payload = Array.isArray(customTasks)
    ? normalizeTasksForApi(customTasks)
    : (customTasks?.tasks ? customTasks : normalizeTasksForApi(
        Object.entries(customTasks || {}).flatMap(([qId, list]) => (Array.isArray(list) ? list.map(t => ({ ...t, taskType: qId })) : []))
      ));

  if (preferRealApi) {
    let res;
    try {
      res = await fetch(`${API_BASE}/custom-workload/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    } catch (netErr) {
      throw new Error(`Unable to connect to FastAPI backend at ${API_BASE}/custom-workload/analyze.`);
    }
    if (!res.ok) throw new Error(await parseErrorResponse(res, 'Custom workload analysis failed'));
    return await res.json();
  }

  // Deterministic browser fallback using the same demand-band thresholds.
  const canonical = { teller: 20, loans: 4.8, customer_service: 10 };
  const rates = {
    teller: (payload.teller || []).reduce((s, t) => s + Number(t.customers_per_hour || 0), 0),
    loans: (payload.loans || []).reduce((s, t) => s + Number(t.customers_per_hour || 0), 0),
    customer_service: (payload.customer_service || []).reduce((s, t) => s + Number(t.customers_per_hour || 0), 0)
  };
  const multiplier = (rates.teller + rates.loans + rates.customer_service) /
    (canonical.teller + canonical.loans + canonical.customer_service || 1);
  const scenarioName = multiplier < 1.35 ? 'normal' : multiplier < 2.25 ? 'peak' : 'surge';
  const scenario = SCENARIOS[scenarioName] || SCENARIOS.normal;
  return {
    scenario: scenario,
    scenario_label: scenarioName === 'normal' ? 'Normal demand' : scenarioName === 'peak' ? 'Peak demand' : 'Surge demand',
    demand_multiplier: Number(multiplier.toFixed(2)),
    forecast: scenario.forecast,
    optimization: {
      scenario_name: scenarioName,
      baseline: scenario.baseline,
      optimized: scenario.optimized,
      score_breakdown: scenario.score_breakdown,
      improvement: scenario.improvement,
      explanation: 'Browser fallback used. Start FastAPI for task-derived forecasting and authoritative optimization.',
      feasible: scenario.feasible,
      forecast: scenario.forecast
    }
  };
}

/** Simulate allocation */
export async function simulateAllocation(scenarioConfig, forecast, allocation) {
  if (preferRealApi) {
    let res;
    try {
      res = await fetch(`${API_BASE}/simulate`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario: scenarioConfig, forecast, allocation })
      });
    } catch (netErr) {
      throw new Error(`Unable to connect to FastAPI backend at ${API_BASE}/simulate.`);
    }
    if (!res.ok) throw new Error(await parseErrorResponse(res, 'Simulation API failed'));
    return await res.json();
  }
  await new Promise(r => setTimeout(r, 150));
  const sc = SCENARIOS[forecast?.scenario_name] || SCENARIOS.surge;
  return sc.baseline.result;
}

/** Run optimizer — FR-API-5 */
export async function optimizeScenario(scenarioConfig, forecast) {
  if (preferRealApi) {
    let res;
    try {
      res = await fetch(`${API_BASE}/optimize`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario: scenarioConfig, forecast })
      });
    } catch (netErr) {
      throw new Error(`Unable to connect to FastAPI backend at ${API_BASE}/optimize.`);
    }
    if (!res.ok) throw new Error(await parseErrorResponse(res, 'Optimizer API failed'));
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
    feasible: sc.feasible
  };
}

/** What-If Simulation — FR-API-6 */
export async function simulateWhatIf(scenarioConfig, forecast, allocationPlan, queuesConfig) {
  if (preferRealApi) {
    let res;
    try {
      res = await fetch(`${API_BASE}/whatif`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario: scenarioConfig, forecast, allocation: allocationPlan })
      });
    } catch (netErr) {
      throw new Error(`Unable to connect to FastAPI backend at ${API_BASE}/whatif.`);
    }
    if (!res.ok) throw new Error(await parseErrorResponse(res, 'What-If simulation failed'));
    return await res.json();
  }

  await new Promise(r => setTimeout(r, 100));
  const staffMap = allocationPlan.staff_by_queue;
  const arrivalsMap = forecast.expected_arrivals;
  const queues = queuesConfig || SCENARIOS.surge.queues;
  const perQueue = {};
  let totalServed = 0, totalOverloaded = 0, weightedWaitSum = 0, totalArrivals = 0, maxP95 = 0;

  queues.forEach(q => {
    const qid = q.queue_id;
    const staff = Math.max(1, staffMap[qid] || 1);
    const arrivals = arrivalsMap[qid] || [];
    const qArrivalTotal = arrivals.reduce((a, b) => a + b, 0);
    totalArrivals += qArrivalTotal;
    const slotCapacity = (15.0 / q.avg_service_time_minutes) * staff;
    let queueOverloads = [], currentBacklog = 0, slotWaits = [];
    arrivals.forEach((arrived, idx) => {
      currentBacklog += arrived;
      const served = Math.min(currentBacklog, slotCapacity);
      currentBacklog -= served;
      const waitEst = slotCapacity > 0 ? (currentBacklog / slotCapacity) * 15 : 30;
      slotWaits.push(waitEst);
      if (waitEst > 10.0 || arrived > slotCapacity * 1.1) queueOverloads.push(forecast.slots[idx]);
    });
    const avgWait = slotWaits.reduce((a, b) => a + b, 0) / (slotWaits.length || 1);
    const sortedWaits = [...slotWaits].sort((a, b) => a - b);
    const p95Wait = sortedWaits[Math.floor(sortedWaits.length * 0.95)] || avgWait * 1.8;
    const utilization = Math.min(0.99, (qArrivalTotal * q.avg_service_time_minutes) / (staff * 8 * 60));
    perQueue[qid] = {
      avg_wait_minutes: parseFloat(avgWait.toFixed(1)), p95_wait_minutes: parseFloat(p95Wait.toFixed(1)),
      utilization: parseFloat(utilization.toFixed(2)), overloaded_slots: queueOverloads,
      total_served: Math.max(0, qArrivalTotal - currentBacklog), end_backlog: currentBacklog
    };
    weightedWaitSum += avgWait * qArrivalTotal;
    totalServed += (qArrivalTotal - currentBacklog);
    totalOverloaded += queueOverloads.length;
    if (p95Wait > maxP95) maxP95 = p95Wait;
  });

  const branchAvgWait = totalArrivals > 0 ? weightedWaitSum / totalArrivals : 4.0;
  return {
    allocation_label: 'whatif', per_queue: perQueue,
    branch_wide: {
      avg_wait_minutes: parseFloat(branchAvgWait.toFixed(1)), p95_wait_minutes: parseFloat(maxP95.toFixed(1)),
      overloaded_slot_count: totalOverloaded, total_served: totalServed,
      total_end_backlog: Object.values(perQueue).reduce((a, b) => a + b.end_backlog, 0)
    }
  };
}

/** ---------------------------------------------------------------------------
 * Persistence & Branch Task APIs (Supabase Backend)
 * --------------------------------------------------------------------------- */

export async function fetchPersistenceStatus() {
  try {
    const res = await fetch(`${API_BASE}/persistence/status`);
    if (res.ok) return await res.json();
  } catch (_) {}
  return { connected: true, mode: 'local_fallback', message: 'Offline browser mode' };
}

export async function fetchBranches() {
  try {
    const res = await fetch(`${API_BASE}/branches`);
    if (res.ok) return await res.json();
  } catch (_) {}
  return [{ id: 'branch-main', name: 'Downtown Main Branch', location: 'Financial District, Metro Central' }];
}

export async function fetchBranchTasks(branchId = 'branch-main') {
  try {
    const res = await fetch(`${API_BASE}/branches/${branchId}/tasks`);
    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data) && data.length > 0) {
        return data.map(t => ({
          id: t.id,
          taskType: t.task_type,
          taskName: t.task_name,
          customersPerHour: Number(t.customers_per_hour),
          averageServiceTimeMinutes: Number(t.average_service_time_minutes)
        }));
      }
    }
  } catch (_) {}
  return null;
}

export async function createBranchTask(branchId = 'branch-main', task) {
  try {
    const res = await fetch(`${API_BASE}/branches/${branchId}/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        taskType: task.taskType,
        taskName: task.taskName,
        customersPerHour: Number(task.customersPerHour),
        averageServiceTimeMinutes: Number(task.averageServiceTimeMinutes)
      })
    });
    if (res.ok) return await res.json();
  } catch (_) {}
  return { ...task, id: `local-${Date.now()}` };
}

export async function updateBranchTask(branchId = 'branch-main', taskId, updates) {
  try {
    const res = await fetch(`${API_BASE}/branches/${branchId}/tasks/${taskId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates)
    });
    if (res.ok) return await res.json();
  } catch (_) {}
  return updates;
}

export async function deleteBranchTask(branchId = 'branch-main', taskId) {
  try {
    const res = await fetch(`${API_BASE}/branches/${branchId}/tasks/${taskId}`, {
      method: 'DELETE'
    });
    if (res.ok) return await res.json();
  } catch (_) {}
  return { status: 'deleted', task_id: taskId };
}

/** ---------------------------------------------------------------------------
 * Branch Stress Test API
 * --------------------------------------------------------------------------- */
export async function runStressTest(branchId = 'branch-main', tasks = null, stressConfig = null) {
  const payload = {
    branch_id: branchId,
    tasks: tasks ? tasks.map(t => ({
      taskType: t.taskType,
      taskName: t.taskName,
      customersPerHour: Number(t.customersPerHour),
      averageServiceTimeMinutes: Number(t.averageServiceTimeMinutes)
    })) : null,
    stress_config: stressConfig || { category: 'demand_shock', seed: 42 }
  };

  if (preferRealApi) {
    let res;
    try {
      res = await fetch(`${API_BASE}/stress-test`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    } catch (netErr) {
      throw new Error(`Unable to connect to backend at ${API_BASE}/stress-test.`);
    }
    if (!res.ok) throw new Error(await parseErrorResponse(res, 'Stress test failed'));
    return await res.json();
  }

  // Browser mock fallback if offline
  await new Promise(r => setTimeout(r, 200));
  return {
    baseline: {
      scenarioClassification: 'normal',
      demandMultiplier: 1.0,
      allocation: { teller: 4, loans: 2, customer_service: 4 },
      averageWait: 4.2,
      overloadedSlots: 0,
      totalStaff: 10
    },
    stressCategory: stressConfig?.category || 'demand_shock',
    stressScenarios: [
      { id: 'd-100', label: 'Baseline (1.00×)', demandMultiplier: 1.0, averageWait: 4.2, overloadedSlots: 0, utilization: 0.62, failure: false, bottleneck: 'Teller' },
      { id: 'd-125', label: '+25% Demand (1.25×)', demandMultiplier: 1.25, averageWait: 7.8, overloadedSlots: 1, utilization: 0.78, failure: false, bottleneck: 'Teller' },
      { id: 'd-150', label: '+50% Demand (1.50×)', demandMultiplier: 1.50, averageWait: 14.1, overloadedSlots: 4, utilization: 0.89, failure: false, bottleneck: 'Teller' },
      { id: 'd-175', label: '+75% Demand (1.75×)', demandMultiplier: 1.75, averageWait: 26.5, overloadedSlots: 9, utilization: 0.96, failure: true, bottleneck: 'Teller' },
      { id: 'd-200', label: '+100% Demand (2.00×)', demandMultiplier: 2.00, averageWait: 41.8, overloadedSlots: 15, utilization: 0.99, failure: true, bottleneck: 'Teller' }
    ],
    breakpoint: {
      multiplier: 1.68,
      label: '~1.68× demand',
      failureReason: 'Overload threshold breached at ~1.68× with Teller queue saturation.',
      bottleneck: 'Teller'
    },
    bottleneck: {
      queue: 'teller',
      queue_name: 'Teller',
      reason: 'Teller experienced 9 overloaded slots with average wait rising from 4.2m to 26.5m.',
      metric: 'avg_wait_minutes',
      baselineValue: 4.2,
      stressedValue: 26.5
    },
    resilienceScore: 81,
    resilienceDetails: {
      score: 81,
      max_score: 100,
      contributors: [
        { factor: 'Demand Headroom', score: 27.2, max: 40, rating: 'strong', description: 'Stable operation sustained up to 1.68× baseline demand.' },
        { factor: 'Overload Resistance', score: 23.4, max: 25, rating: 'strong', description: 'Overload incidence restricted under moderate shock.' },
        { factor: 'Queue Stability', score: 17.5, max: 20, rating: 'strong', description: 'Customer wait escalation ratio is controlled.' },
        { factor: 'Workforce Flexibility', score: 13.0, max: 15, rating: 'strong', description: 'Staffing reallocation margin allows dynamic response.' }
      ]
    },
    recoveryPlans: [
      {
        id: 'plan-optimal-reallocation',
        title: 'Optimal Workforce Reallocation',
        strategy: 'reallocate',
        action: 'Move 1 Customer Service → Teller',
        resulting_allocation: { teller: 5, loans: 2, customer_service: 3 },
        staffing_change: { teller: 1, customer_service: -1, loans: 0 },
        average_wait_minutes: 11.2,
        overloaded_slots: 2,
        wait_reduction_minutes: 15.3,
        overload_reduction_count: 7,
        disruption_score: 2,
        feasibility: 'Fully Feasible (Budget Neutral)'
      }
    ],
    assumptions: {
      simulationSlotMinutes: 15,
      criticalWaitThresholdMinutes: 15.0,
      seed: 42,
      methodology: 'Deterministic fixed-step simulation with binary search breakpoint estimation'
    }
  };
}

/** ---------------------------------------------------------------------------
 * Scenario Runs & History Persistence APIs
 * --------------------------------------------------------------------------- */
export async function saveScenario(payload) {
  if (preferRealApi) {
    let res;
    try {
      res = await fetch(`${API_BASE}/scenarios`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
    } catch (netErr) {
      throw new Error(`Unable to connect to backend at ${API_BASE}/scenarios.`);
    }
    if (!res.ok) throw new Error(await parseErrorResponse(res, 'Failed to save scenario'));
    return await res.json();
  }

  return {
    id: `scenario-${Date.now()}`,
    branch_id: payload.branch_id || 'branch-main',
    scenario_type: payload.scenario_type,
    scenario_name: payload.scenario_name,
    created_at: new Date().toISOString()
  };
}

export async function fetchScenarioHistory(branchId = 'branch-main', scenarioType = null) {
  try {
    const url = scenarioType
      ? `${API_BASE}/branches/${branchId}/scenarios?scenario_type=${scenarioType}`
      : `${API_BASE}/branches/${branchId}/scenarios`;
    const res = await fetch(url);
    if (res.ok) return await res.json();
  } catch (_) {}
  return [];
}
