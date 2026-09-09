import React, { useState, useEffect } from 'react';

export default function WhatIfSimulator({
  queues = [],
  totalStaffBudget = 10,
  initialAllocation = {},
  onRunWhatIf,
  whatIfResult,
  loading
}) {
  const [allocation, setAllocation] = useState({});

  useEffect(() => {
    if (initialAllocation && Object.keys(initialAllocation).length > 0) {
      setAllocation(initialAllocation);
    } else {
      setAllocation({ teller: 4, loans: 2, customer_service: 2, cashier: 2 });
    }
  }, [initialAllocation]);

  const currentTotal = Object.values(allocation).reduce((a, b) => a + (parseInt(b, 10) || 0), 0);
  const isValidBudget = currentTotal === totalStaffBudget;

  const handleStep = (qid, delta) => {
    setAllocation(prev => {
      const current = prev[qid] || 1;
      const qConfig = queues.find(q => q.queue_id === qid);
      const minStaff = qConfig?.min_staff ?? 1;
      const maxStaff = qConfig?.max_staff ?? 6;
      const nextVal = Math.min(maxStaff, Math.max(minStaff, current + delta));
      return { ...prev, [qid]: nextVal };
    });
  };

  const handleRun = () => {
    if (isValidBudget && onRunWhatIf) {
      onRunWhatIf(allocation);
    }
  };

  const whatIfMetrics = whatIfResult?.branch_wide;
  const avgWait = whatIfMetrics?.avg_wait_minutes;
  const p95Wait = whatIfMetrics?.p95_wait_minutes;
  const utilization = whatIfMetrics?.avg_utilization ?? (whatIfMetrics?.utilization ?? 0);
  const utilPercent = Math.round(utilization * 100);
  const overloadedSlots = whatIfMetrics?.overloaded_slot_count;

  return (
    <section className="vortex-section what-if-section" id="what-if">
      <div className="section-title-wrap">
        <span className="section-cyan-indicator" />
        <h2 className="section-heading">WHAT-IF SIMULATOR</h2>
        <span className="section-sub-tag">TEST ALTERNATIVE STAFF ALLOCATIONS</span>
      </div>

      <div className="vortex-card what-if-card">
        <div className="what-if-header-bar">
          <div className="simulation-notice-badge font-mono">
            <span>● EXPERIMENTAL SIMULATION ONLY</span>
          </div>
          <div className={`budget-status-tag font-mono ${isValidBudget ? 'valid' : 'invalid'}`}>
            STAFF BUDGET: {currentTotal} / {totalStaffBudget}
          </div>
        </div>

        {/* Stepper Controls Per Queue */}
        <div className="what-if-queues-grid">
          {queues.map((q) => {
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
                  <span className="staff-label">CURRENT STAFF</span>
                  <div className="stepper-wrap">
                    <button
                      className="stepper-btn minus"
                      onClick={() => handleStep(qid, -1)}
                      disabled={count <= minStaff}
                      aria-label={`Decrease ${q.name} staff`}
                    >
                      −
                    </button>
                    <span className="stepper-val font-mono cyan">{count}</span>
                    <button
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

        {/* Hard Constraint Feedback */}
        {!isValidBudget && (
          <div className="constraint-error-alert font-mono">
            <span className="error-icon">⚠</span>
            <span>HARD RESOURCE CONSTRAINT VIOLATED: Total staff must equal {totalStaffBudget} (currently allocated: {currentTotal}).</span>
          </div>
        )}

        {/* Action Button: [ RUN WHAT-IF ] */}
        <div className="what-if-action-row">
          <button
            className="cmd-btn-primary full-width"
            onClick={handleRun}
            disabled={!isValidBudget || loading}
          >
            {loading ? (
              <>
                <span className="btn-spinner" />
                <span>SIMULATING QUEUE LOAD...</span>
              </>
            ) : (
              <span>RUN WHAT-IF</span>
            )}
          </button>
        </div>

        {/* Simulation Output Metrics */}
        {whatIfMetrics ? (
          <div className="what-if-results-box">
            <div className="results-box-title font-mono">
              <span>SIMULATION OUTCOME // EXPERIMENTAL TELEMETRY</span>
            </div>
            <div className="results-metrics-grid">
              
              <div className="res-metric-cell">
                <span className="res-metric-label font-mono">AVG WAIT</span>
                <span className="res-metric-val font-mono green">{avgWait?.toFixed(1)} MIN</span>
                <span className="res-sub font-mono">SIMULATED AVERAGE</span>
              </div>

              <div className="res-metric-cell">
                <span className="res-metric-label font-mono">P95 WAIT</span>
                <span className="res-metric-val font-mono cyan">{(p95Wait ?? 0).toFixed(1)} MIN</span>
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
            <span>AWAITING INPUT — ADJUST STAFF AND CLICK [ RUN WHAT-IF ] TO EVALUATE</span>
          </div>
        )}
      </div>
    </section>
  );
}
