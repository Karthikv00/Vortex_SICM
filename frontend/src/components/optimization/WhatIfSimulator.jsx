import React, { useState, useEffect } from 'react';
import { formatDuration } from '../../utils/formatters';
import TaskWorkloadEditor from '../common/TaskWorkloadEditor';

export default function WhatIfSimulator({
  queues = [],
  totalStaffBudget = 10,
  initialAllocation = null,
  onRunWhatIf,
  whatIfResult,
  loading,
  whatIfTasks = [],
  onWhatIfTasksChange,
  onRunWhatIfWorkload,
  whatIfAnalysis = null,
  whatIfWorkloadLoading = false,
  onApplyWhatIfToLive
}) {
  const [activeTab, setActiveTab] = useState('workload'); // 'workload' | 'staffing'
  const [allocation, setAllocation] = useState({});
  const allocationKey = initialAllocation ? JSON.stringify(initialAllocation) : '';

  useEffect(() => {
    if (initialAllocation && Object.keys(initialAllocation).length > 0) {
      setAllocation({ ...initialAllocation });
    }
  }, [allocationKey]);

  const currentTotal = Object.values(allocation).reduce((a, b) => a + (parseInt(b, 10) || 0), 0);
  const isValidBudget = currentTotal === totalStaffBudget;

  const handleStep = (qid, delta) => setAllocation(prev => {
    const current = prev[qid] || 1;
    const qConfig = queues.find(q => q.queue_id === qid);
    return { ...prev, [qid]: Math.min(qConfig?.max_staff ?? 6, Math.max(qConfig?.min_staff ?? 1, current + delta)) };
  });

  const handleRunStaffing = () => {
    if (isValidBudget && onRunWhatIf) onRunWhatIf(allocation);
  };

  const whatIfMetrics = whatIfResult?.branch_wide;
  const avgWait = whatIfMetrics?.avg_wait_minutes;
  const p95Wait = whatIfMetrics?.p95_wait_minutes;
  const queueUtils = whatIfResult?.per_queue ? Object.values(whatIfResult.per_queue).map(q => q.utilization ?? 0) : [];
  const meanUtil = queueUtils.length ? queueUtils.reduce((a, b) => a + b, 0) / queueUtils.length : 0;
  const utilization = whatIfMetrics?.avg_utilization ?? meanUtil;
  const utilPercent = Math.round(utilization * 100);
  const overloadedSlots = whatIfMetrics?.overloaded_slot_count ?? 0;

  return (
    <section className="vortex-section what-if-section" id="what-if">
      <div className="section-title-wrap">
        <span className="section-cyan-indicator" />
        <h2 className="section-heading">WHAT-IF SIMULATOR</h2>
        <span className="section-sub-tag">HYPOTHETICAL WORKLOAD & ALLOCATION EXPERIMENTS</span>
      </div>

      <div className="vortex-card what-if-card">
        <div className="what-if-header-bar">
          <div className="simulation-notice-badge font-mono">
            <span>● EXPERIMENTAL SIMULATION ONLY — DOES NOT ALTER LIVE BRANCH STATE</span>
          </div>
          <div className="what-if-tab-toggles font-mono">
            <button
              type="button"
              className={`what-if-toggle-btn ${activeTab === 'workload' ? 'active' : ''}`}
              onClick={() => setActiveTab('workload')}
            >
              HYPOTHETICAL DEMAND WORKLOAD
            </button>
            <button
              type="button"
              className={`what-if-toggle-btn ${activeTab === 'staffing' ? 'active' : ''}`}
              onClick={() => setActiveTab('staffing')}
            >
              STAFF REALLOCATION
            </button>
          </div>
        </div>

        {activeTab === 'workload' ? (
          <div className="what-if-workload-pane">
            <TaskWorkloadEditor
              tasks={whatIfTasks}
              onChange={onWhatIfTasksChange}
              onSubmit={onRunWhatIfWorkload}
              submitting={whatIfWorkloadLoading}
              submitLabel="SIMULATE WHAT-IF WORKLOAD"
              isWhatIf={true}
              title="WHAT-IF SCENARIO DEMAND"
              subtitle="Test hypothetical customer demand spikes or task reconfigurations without modifying live operations. The decision pipeline computes the hypothetical scenario, forecast, overload risk, and optimal staffing."
              analysis={whatIfAnalysis}
            />

            {whatIfAnalysis && (
              <div className="what-if-hypothetical-summary font-mono">
                <div className="hypothetical-summary-header">
                  <span className="cyan bold">HYPOTHETICAL PIPELINE TELEMETRY</span>
                  {onApplyWhatIfToLive && (
                    <button
                      type="button"
                      className="cmd-btn-primary apply-live-btn"
                      onClick={onApplyWhatIfToLive}
                    >
                      ✓ APPLY THIS SCENARIO TO LIVE BRANCH
                    </button>
                  )}
                </div>

                <div className="results-metrics-grid">
                  <div className="res-metric-cell">
                    <span className="res-metric-label font-mono">PROJECTED AVG WAIT</span>
                    <span className="res-metric-val font-mono green">
                      {formatDuration(whatIfAnalysis.optimization?.optimized?.result?.branch_wide?.avg_wait_minutes ?? 0)}
                    </span>
                    <span className="res-sub font-mono">HYPOTHETICAL OPTIMIZED</span>
                  </div>
                  <div className="res-metric-cell">
                    <span className="res-metric-label font-mono">PROJECTED P95 WAIT</span>
                    <span className="res-metric-val font-mono cyan">
                      {formatDuration(whatIfAnalysis.optimization?.optimized?.result?.branch_wide?.p95_wait_minutes ?? 0)}
                    </span>
                    <span className="res-sub font-mono">TAIL LATENCY</span>
                  </div>
                  <div className="res-metric-cell">
                    <span className="res-metric-label font-mono">CAPACITY RATIO</span>
                    <span className="res-metric-val font-mono yellow">
                      {Math.round((whatIfAnalysis.optimization?.optimized?.result?.branch_wide?.avg_utilization ?? 0.7) * 100)}%
                    </span>
                    <span className="res-sub font-mono">SYSTEM CAPACITY</span>
                  </div>
                  <div className="res-metric-cell">
                    <span className="res-metric-label font-mono">OVERLOAD SLOTS</span>
                    <span className={`res-metric-val font-mono ${(whatIfAnalysis.optimization?.optimized?.result?.branch_wide?.overloaded_slot_count ?? 0) > 0 ? 'critical' : 'green'}`}>
                      {whatIfAnalysis.optimization?.optimized?.result?.branch_wide?.overloaded_slot_count ?? 0} SLOTS
                    </span>
                    <span className="res-sub font-mono">CONGESTION INTERVALS</span>
                  </div>
                </div>

                {whatIfAnalysis.optimization?.optimized?.allocation?.staff_by_queue && (
                  <div className="hypothetical-staffing-pill-row">
                    <span className="text-muted">RECOMMENDED HYPOTHETICAL STAFFING:</span>
                    {Object.entries(whatIfAnalysis.optimization.optimized.allocation.staff_by_queue).map(([qid, count]) => (
                      <span key={qid} className="hypo-staff-tag font-mono">
                        {qid.toUpperCase()}: <strong className="cyan">{count} AGENTS</strong>
                      </span>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        ) : (
          <div className="what-if-staffing-pane">
            <div className={`budget-status-tag font-mono ${isValidBudget ? 'valid' : 'invalid'}`}>
              STAFF BUDGET: {currentTotal} / {totalStaffBudget}
            </div>
            <div className="what-if-queues-grid">
              {queues.map(q => {
                const qid = q.queue_id;
                const count = allocation[qid] || 1;
                const minStaff = q.min_staff ?? 1;
                const maxStaff = q.max_staff ?? 6;
                return (
                  <div key={qid} className="what-if-queue-row">
                    <div className="what-if-q-info">
                      <span className="what-if-q-code font-mono">{qid.toUpperCase()}</span>
                      <h4 className="what-if-q-name">{q.name}</h4>
                      <span className="what-if-q-range font-mono">BOUNDS: {minStaff} — {maxStaff}</span>
                    </div>
                    <div className="what-if-current-staff">
                      <span className="staff-label">HYPOTHETICAL STAFF</span>
                      <div className="stepper-wrap">
                        <button
                          type="button"
                          className="stepper-btn minus"
                          onClick={() => handleStep(qid, -1)}
                          disabled={count <= minStaff}
                          aria-label={`Decrease ${q.name} staff`}
                        >
                          −
                        </button>
                        <span className="stepper-val font-mono cyan">{count}</span>
                        <button
                          type="button"
                          className="stepper-btn plus"
                          onClick={() => handleStep(qid, 1)}
                          disabled={count >= maxStaff}
                          aria-label={`Increase ${q.name} staff`}
                        >
                          +
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>

            {!isValidBudget && (
              <div className="constraint-error-alert font-mono">
                <span className="error-icon">⚠</span>
                <span>HARD RESOURCE CONSTRAINT VIOLATED: Total staff must equal {totalStaffBudget} (currently allocated: {currentTotal}).</span>
              </div>
            )}

            <div className="what-if-action-row">
              <button
                type="button"
                className="cmd-btn-primary full-width"
                onClick={handleRunStaffing}
                disabled={!isValidBudget || loading}
              >
                {loading ? (
                  <>
                    <span className="btn-spinner" />
                    <span>SIMULATING QUEUE LOAD...</span>
                  </>
                ) : (
                  <span>RUN WHAT-IF SIMULATION</span>
                )}
              </button>
            </div>

            {whatIfMetrics ? (
              <div className="what-if-results-box">
                <div className="results-box-title font-mono">
                  <span>SIMULATION OUTCOME // EXPERIMENTAL TELEMETRY</span>
                </div>
                <div className="results-metrics-grid">
                  <div className="res-metric-cell">
                    <span className="res-metric-label font-mono">AVG WAIT</span>
                    <span className="res-metric-val font-mono green">{formatDuration(avgWait)}</span>
                    <span className="res-sub font-mono">SIMULATED AVERAGE</span>
                  </div>
                  <div className="res-metric-cell">
                    <span className="res-metric-label font-mono">P95 WAIT</span>
                    <span className="res-metric-val font-mono cyan">{formatDuration(p95Wait)}</span>
                    <span className="res-sub font-mono">TAIL LATENCY</span>
                  </div>
                  <div className="res-metric-cell">
                    <span className="res-metric-label font-mono">UTILIZATION</span>
                    <span className="res-metric-val font-mono yellow">{utilPercent}%</span>
                    <span className="res-sub font-mono">SYSTEM CAPACITY</span>
                  </div>
                  <div className="res-metric-cell">
                    <span className="res-metric-label font-mono">OVERLOADED SLOTS</span>
                    <span className={`res-metric-val font-mono ${overloadedSlots > 0 ? 'critical' : 'green'}`}>
                      {overloadedSlots} SLOTS
                    </span>
                    <span className="res-sub font-mono">CONGESTION INTERVALS</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="what-if-placeholder font-mono">
                <span>AWAITING INPUT — ADJUST STAFF AND CLICK [ RUN WHAT-IF SIMULATION ] TO EVALUATE</span>
              </div>
            )}
          </div>
        )}
      </div>
    </section>
  );
}
