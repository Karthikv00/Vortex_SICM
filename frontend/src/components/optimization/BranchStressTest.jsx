import React, { useState } from 'react';
import { runStressTest, saveScenario } from '../../services/api';

export default function BranchStressTest({
  tasks = [],
  branchId = 'branch-main',
  onScenarioSaved,
  onInspectScenario,
  inspectedScenario = null
}) {
  const [category, setCategory] = useState('demand_shock');
  const [running, setRunning] = useState(false);
  const [stressResult, setStressResult] = useState(null);
  const [error, setError] = useState(null);

  // Saving scenario state
  const [scenarioName, setScenarioName] = useState('');
  const [saving, setSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  const displayResult = inspectedScenario ? inspectedScenario.result_snapshot : stressResult;

  const handleRunStressTest = async () => {
    setRunning(true);
    setError(null);
    setSaveSuccess(false);
    try {
      const res = await runStressTest(branchId, tasks, { category, seed: 42 });
      setStressResult(res);
      // Auto-populate default name for saving
      const catLabel = category === 'demand_shock' ? 'Demand Shock'
        : category === 'service_time_shock' ? 'Service Duration Shock'
        : category === 'workforce_shock' ? 'Workforce Absence'
        : 'Combined Shock';
      setScenarioName(`${catLabel} — Score ${res.resilienceScore} (${res.bottleneck?.queue_name || 'Bottleneck'})`);
    } catch (err) {
      setError(err.message || 'Failed to execute branch stress test.');
    } finally {
      setRunning(false);
    }
  };

  const handleSaveScenario = async (e) => {
    e.preventDefault();
    if (!displayResult || !scenarioName.trim() || saving) return;
    setSaving(true);
    try {
      await saveScenario({
        branch_id: branchId,
        scenario_type: 'stress_test',
        scenario_name: scenarioName.trim(),
        input_snapshot: {
          category: displayResult.stressCategory || category,
          tasks_count: tasks?.length || 0,
          tasks_summary: tasks?.map(t => `${t.taskName} (${t.customersPerHour}/h)`).join(', ')
        },
        result_snapshot: displayResult
      });
      setSaveSuccess(true);
      if (onScenarioSaved) onScenarioSaved();
    } catch (err) {
      setError('Could not save scenario run to persistence storage.');
    } finally {
      setSaving(false);
    }
  };

  // SVG Chart Dimensions
  const svgWidth = 620;
  const svgHeight = 220;
  const padLeft = 45;
  const padRight = 30;
  const padTop = 25;
  const padBottom = 35;

  const scenarios = displayResult?.stressScenarios || [];
  const maxWait = Math.max(10, ...scenarios.map(s => s.averageWait || 0));
  const maxMult = Math.max(1.5, ...scenarios.map(s => s.demandMultiplier || s.serviceTimeMultiplier || 1.0));
  const minMult = Math.min(1.0, ...scenarios.map(s => s.demandMultiplier || s.serviceTimeMultiplier || 1.0));

  const getX = (mult) => {
    if (maxMult === minMult) return padLeft + 50;
    return padLeft + ((mult - minMult) / (maxMult - minMult)) * (svgWidth - padLeft - padRight);
  };

  const getY = (val) => {
    return svgHeight - padBottom - (val / (maxWait * 1.15)) * (svgHeight - padTop - padBottom);
  };

  const points = scenarios.map(s => {
    const mult = s.demandMultiplier || s.serviceTimeMultiplier || (1.0 + (s.unavailableStaff || 0) * 0.2);
    return {
      x: getX(mult),
      y: getY(s.averageWait || 0),
      mult,
      wait: s.averageWait,
      overload: s.overloadedSlots,
      fail: s.failure,
      label: s.label
    };
  });

  const pathD = points.length > 0
    ? points.reduce((acc, p, idx) => `${acc} ${idx === 0 ? 'M' : 'L'} ${p.x} ${p.y}`, '')
    : '';

  const bpMult = displayResult?.breakpoint?.multiplier || 1.0;
  const bpX = getX(bpMult);
  const bpY = getY(displayResult?.breakpoint?.multiplier ? (maxWait * 0.6) : 0);

  return (
    <section className="vortex-section branch-stress-section" id="stress-test">
      <div className="section-title-wrap">
        <span className="section-cyan-indicator" />
        <h2 className="section-heading">BRANCH STRESS TEST & RESILIENCE ENGINE</h2>
        <span className="section-sub-tag">BREAKPOINT DETECTION & RECOVERY</span>
      </div>

      <div className="vortex-card stress-test-card">
        {/* Header & Controls */}
        <div className="stress-card-header">
          <div className="stress-desc-block">
            <h3 className="stress-main-title">Stress Simulation & Dynamic Breaking Point Analysis</h3>
            <p className="stress-main-desc">
              Progressively stress branch demand, service durations, and staffing to calculate the exact
              simulated operational breakpoint, pinpoint the primary queue bottleneck, and evaluate feasible recovery plans.
            </p>
          </div>

          <div className="stress-controls-wrap">
            <div className="stress-category-picker">
              <label className="stress-control-label">STRESS CATEGORY</label>
              <select
                className="vortex-select stress-category-select"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                disabled={running}
              >
                <option value="demand_shock">Demand Shock (1.00× → 2.00×)</option>
                <option value="service_time_shock">Service-Time Shock (1.00× → 1.50×)</option>
                <option value="workforce_shock">Workforce Shock (1–2 Staff Absent)</option>
                <option value="combined_shock">Combined Shock (+50% D, +20% S, -1 Staff)</option>
              </select>
            </div>

            <button
              className="vortex-btn primary-btn run-stress-btn font-mono"
              onClick={handleRunStressTest}
              disabled={running || (tasks && tasks.length === 0)}
            >
              {running ? (
                <>
                  <span className="spinner-dot" />
                  EVALUATING BREAKING POINT...
                </>
              ) : (
                'RUN BRANCH STRESS TEST'
              )}
            </button>
          </div>
        </div>

        {error && (
          <div className="stress-error-banner font-mono">
            <strong>STRESS TEST ALERT:</strong> {error}
          </div>
        )}

        {inspectedScenario && (
          <div className="inspected-banner font-mono">
            <span>INSPECTING SAVED SCENARIO: <strong>{inspectedScenario.scenario_name}</strong></span>
            <button className="banner-close-btn" onClick={() => onInspectScenario && onInspectScenario(null)}>
              EXIT INSPECTION
            </button>
          </div>
        )}

        {/* Results Canvas */}
        {displayResult && (
          <div className="stress-results-canvas">
            {/* Top KPIs */}
            <div className="stress-kpi-grid">
              {/* Resilience Score */}
              <div className="stress-kpi-card resilience-kpi">
                <div className="kpi-tag font-mono">BRANCH RESILIENCE</div>
                <div className="resilience-score-wrap">
                  <span className="score-num font-mono">{displayResult.resilienceScore}</span>
                  <span className="score-denom font-mono">/ 100</span>
                </div>
                <div className="resilience-bar-track">
                  <div
                    className="resilience-bar-fill"
                    style={{
                      width: `${displayResult.resilienceScore}%`,
                      backgroundColor: displayResult.resilienceScore >= 80 ? 'var(--cyan-glow)' : displayResult.resilienceScore >= 60 ? 'var(--amber-warn)' : 'var(--magenta-alert)'
                    }}
                  />
                </div>
                <div className="resilience-factors-list">
                  {displayResult.resilienceDetails?.contributors?.map((c, i) => (
                    <div key={i} className="resilience-factor-item font-mono">
                      <span className="factor-name">{c.factor}:</span>
                      <span className={`factor-rating rating-${c.rating}`}>{c.rating.toUpperCase()}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Breakpoint */}
              <div className="stress-kpi-card breakpoint-kpi">
                <div className="kpi-tag font-mono">OPERATIONAL BREAKPOINT</div>
                <div className="breakpoint-value font-mono">
                  {displayResult.breakpoint?.label || `~${displayResult.breakpoint?.multiplier}×`}
                </div>
                <p className="kpi-subtext">
                  {displayResult.breakpoint?.failureReason || 'Simulated threshold where wait time and queue overload breach operational tolerance.'}
                </p>
                <div className="kpi-badge-row font-mono">
                  <span className="badge-tag">SIMULATED BOUNDARY</span>
                  <span className="badge-tag cyan">BISECTION SEARCH</span>
                </div>
              </div>

              {/* Bottleneck */}
              <div className="stress-kpi-card bottleneck-kpi">
                <div className="kpi-tag font-mono">PRIMARY BOTTLENECK</div>
                <div className="bottleneck-queue font-mono text-magenta">
                  {displayResult.bottleneck?.queue_name || displayResult.bottleneck?.queue || 'Teller'}
                </div>
                <p className="kpi-subtext">
                  {displayResult.bottleneck?.reason || 'Primary contributor to operational degradation under stress.'}
                </p>
                <div className="bottleneck-metrics font-mono">
                  <span>Baseline Wait: <strong>{displayResult.bottleneck?.baselineValue ?? 4.2}m</strong></span>
                  <span className="metric-arrow">→</span>
                  <span>Stressed: <strong className="text-magenta">{displayResult.bottleneck?.stressedValue ?? 26.5}m</strong></span>
                </div>
              </div>
            </div>

            {/* 2D Resilience / Stress Progression Curve */}
            <div className="stress-curve-wrapper">
              <div className="curve-header">
                <div className="curve-title-wrap">
                  <span className="font-mono cyan">STRESS DEGRADATION CURVE</span>
                  <span className="curve-legend font-mono">
                    <span className="legend-dot safe" /> Safe Zone
                    <span className="legend-dot warn" /> Warning Zone
                    <span className="legend-dot fail" /> Failure Region
                  </span>
                </div>
                <div className="curve-subtitle font-mono">
                  AVERAGE CUSTOMER WAIT (MINUTES) VS STRESS FACTOR
                </div>
              </div>

              <div className="curve-svg-container">
                <svg
                  className="stress-curve-svg"
                  viewBox={`0 0 ${svgWidth} ${svgHeight}`}
                  preserveAspectRatio="xMidYMid meet"
                >
                  <defs>
                    <linearGradient id="curveStroke" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stopColor="#00F0FF" />
                      <stop offset="65%" stopColor="#FFB800" />
                      <stop offset="100%" stopColor="#FF0055" />
                    </linearGradient>
                    <linearGradient id="zoneGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                      <stop offset="0%" stopColor="rgba(0, 240, 255, 0.25)" />
                      <stop offset="100%" stopColor="rgba(0, 240, 255, 0.0)" />
                    </linearGradient>
                  </defs>

                  {/* Grid Lines */}
                  {[0, 0.25, 0.5, 0.75, 1.0].map((ratio, idx) => {
                    const y = svgHeight - padBottom - ratio * (svgHeight - padTop - padBottom);
                    const val = (ratio * maxWait * 1.15).toFixed(0);
                    return (
                      <g key={idx}>
                        <line
                          x1={padLeft}
                          y1={y}
                          x2={svgWidth - padRight}
                          y2={y}
                          stroke="rgba(255, 255, 255, 0.08)"
                          strokeDasharray="3 3"
                        />
                        <text
                          x={padLeft - 8}
                          y={y + 4}
                          fill="rgba(255, 255, 255, 0.4)"
                          fontSize="10"
                          textAnchor="end"
                          className="font-mono"
                        >
                          {val}m
                        </text>
                      </g>
                    );
                  })}

                  {/* Critical Threshold Line */}
                  <line
                    x1={padLeft}
                    y1={getY(15.0)}
                    x2={svgWidth - padRight}
                    y2={getY(15.0)}
                    stroke="rgba(255, 0, 85, 0.5)"
                    strokeWidth="1.5"
                    strokeDasharray="4 2"
                  />
                  <text
                    x={svgWidth - padRight}
                    y={getY(15.0) - 6}
                    fill="#FF0055"
                    fontSize="9"
                    textAnchor="end"
                    className="font-mono"
                  >
                    15.0m SLA THRESHOLD
                  </text>

                  {/* Connecting Stress Line */}
                  {pathD && (
                    <path
                      d={pathD}
                      fill="none"
                      stroke="url(#curveStroke)"
                      strokeWidth="3"
                      strokeLinecap="round"
                    />
                  )}

                  {/* Data Points */}
                  {points.map((p, idx) => (
                    <g key={idx} className="curve-data-point">
                      <circle
                        cx={p.x}
                        cy={p.y}
                        r={p.fail ? 5 : 4}
                        fill={p.fail ? '#FF0055' : p.wait > 10 ? '#FFB800' : '#00F0FF'}
                        stroke="#0D1117"
                        strokeWidth="2"
                      />
                      <text
                        x={p.x}
                        y={svgHeight - 12}
                        fill="rgba(255, 255, 255, 0.6)"
                        fontSize="10"
                        textAnchor="middle"
                        className="font-mono"
                      >
                        {p.mult.toFixed(2)}×
                      </text>
                    </g>
                  ))}

                  {/* Breakpoint Marker */}
                  {bpX >= padLeft && bpX <= svgWidth - padRight && (
                    <g className="breakpoint-marker-group">
                      <line
                        x1={bpX}
                        y1={padTop}
                        x2={bpX}
                        y2={svgHeight - padBottom}
                        stroke="#FFB800"
                        strokeWidth="2"
                        strokeDasharray="4 4"
                      />
                      <rect
                        x={Math.min(bpX - 45, svgWidth - padRight - 90)}
                        y={padTop - 18}
                        width="90"
                        height="18"
                        rx="3"
                        fill="#FFB800"
                      />
                      <text
                        x={Math.min(bpX, svgWidth - padRight - 45)}
                        y={padTop - 5}
                        fill="#0D1117"
                        fontSize="10"
                        fontWeight="bold"
                        textAnchor="middle"
                        className="font-mono"
                      >
                        BREAKPOINT
                      </text>
                    </g>
                  )}
                </svg>
              </div>
            </div>

            {/* Recovery Plans */}
            <div className="recovery-plans-container">
              <div className="recovery-header">
                <div>
                  <h4 className="recovery-title">FEASIBLE RECOVERY PLAN RECOMMENDATIONS</h4>
                  <p className="recovery-subtitle font-mono">
                    LEAST-DISRUPTIVE OPERATIONAL INTERVENTIONS RANKED BY EFFECTIVENESS
                  </p>
                </div>
              </div>

              <div className="recovery-plans-grid">
                {displayResult.recoveryPlans && displayResult.recoveryPlans.length > 0 ? (
                  displayResult.recoveryPlans.map((plan, idx) => (
                    <div key={plan.id || idx} className={`recovery-card ${idx === 0 ? 'top-ranked' : ''}`}>
                      <div className="plan-rank-badge font-mono">
                        {idx === 0 ? '★ RECOMMENDED INTERVENTION' : `ALTERNATIVE OPTION ${idx + 1}`}
                      </div>
                      <h5 className="plan-title">{plan.title}</h5>
                      <div className="plan-action-text font-mono text-cyan">
                        {plan.action}
                      </div>

                      <div className="plan-impact-metrics">
                        <div className="plan-metric-box">
                          <span className="metric-lbl font-mono">PROJECTED WAIT</span>
                          <span className="metric-val font-mono">{plan.average_wait_minutes}m</span>
                          <span className="metric-delta font-mono text-green">-{plan.wait_reduction_minutes}m</span>
                        </div>
                        <div className="plan-metric-box">
                          <span className="metric-lbl font-mono">OVERLOAD SLOTS</span>
                          <span className="metric-val font-mono">{plan.overloaded_slots}</span>
                          <span className="metric-delta font-mono text-green">-{plan.overload_reduction_count} slots</span>
                        </div>
                        <div className="plan-metric-box">
                          <span className="metric-lbl font-mono">DISRUPTION</span>
                          <span className="metric-val font-mono">{plan.disruption_score} mvts</span>
                          <span className="metric-sub font-mono">{plan.feasibility}</span>
                        </div>
                      </div>

                      <div className="plan-staffing-alloc font-mono">
                        <span className="alloc-label">RESULTING ALLOCATION:</span>
                        {Object.entries(plan.resulting_allocation || {}).map(([q, s]) => (
                          <span key={q} className="alloc-pill">
                            {q}: <strong>{s}</strong>
                          </span>
                        ))}
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="no-plans-msg font-mono">
                    Current allocation is optimal for the evaluated scenario. No further redistribution required.
                  </div>
                )}
              </div>
            </div>

            {/* Save Scenario to Supabase */}
            <div className="save-scenario-strip">
              <form onSubmit={handleSaveScenario} className="save-scenario-form">
                <div className="save-input-group">
                  <label className="save-label font-mono">SAVE SCENARIO SNAPSHOT:</label>
                  <input
                    type="text"
                    className="vortex-input save-input font-mono"
                    placeholder="Enter scenario name e.g. Morning Demand Surge"
                    value={scenarioName}
                    onChange={(e) => setScenarioName(e.target.value)}
                    disabled={saving}
                  />
                </div>
                <button
                  type="submit"
                  className="vortex-btn secondary-btn save-btn font-mono"
                  disabled={saving || !scenarioName.trim()}
                >
                  {saving ? 'PERSISTING TO SUPABASE...' : saveSuccess ? '✓ SCENARIO PERSISTED' : 'SAVE TO SCENARIO HISTORY'}
                </button>
              </form>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
