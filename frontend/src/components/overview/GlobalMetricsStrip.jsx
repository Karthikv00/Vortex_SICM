import React from 'react';

export default function GlobalMetricsStrip({
  simulationResult,
  loading
}) {
  const branchMetrics = simulationResult?.branch_wide;
  const avgWait = branchMetrics?.avg_wait_minutes ?? 0;
  const p95Wait = branchMetrics?.p95_wait_minutes ?? 0;
  const utilization = branchMetrics?.avg_utilization ?? (branchMetrics?.utilization ?? 0);
  const utilPercent = Math.round(utilization * 100);
  const overloadedSlots = branchMetrics?.overloaded_slot_count ?? 0;

  return (
    <section className="vortex-section global-metrics-section" id="global-metrics">
      <div className="metrics-cards-grid">
        
        {/* Metric 1: AVG WAIT (Hero Dark Card inspired by Pinterest reference) */}
        <div className="stat-card hero-dark-card">
          <div className="stat-card-header">
            <span className="stat-label">AVG WAIT TIME</span>
            <span className="stat-badge-trend positive">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" />
                <polyline points="17 6 23 6 23 12" />
              </svg>
              <span>{avgWait <= 8 ? 'Nominal SLA' : 'Exceeding SLA'}</span>
            </span>
          </div>
          <div className="stat-value-wrap">
            {loading ? (
              <span className="stat-loading">--</span>
            ) : (
              <div className="stat-number-row">
                <span className="stat-value font-mono">{avgWait.toFixed(1)}</span>
                <span className="stat-unit">min</span>
              </div>
            )}
          </div>
          <div className="stat-footer-text">
            {avgWait > 8 ? 'High branch congestion detected' : 'Within target operations tolerance'}
          </div>
        </div>

        {/* Metric 2: P95 WAIT */}
        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-label">P95 WAIT TIME</span>
            <span className={`stat-badge-pill ${p95Wait > 15 ? 'critical' : 'normal'}`}>
              Tail Latency
            </span>
          </div>
          <div className="stat-value-wrap">
            {loading ? (
              <span className="stat-loading">--</span>
            ) : (
              <div className="stat-number-row">
                <span className={`stat-value font-mono ${p95Wait > 15 ? 'text-critical' : ''}`}>
                  {p95Wait.toFixed(1)}
                </span>
                <span className="stat-unit">min</span>
              </div>
            )}
          </div>
          <div className="stat-footer-text">
            95% of branch visitors served within this window
          </div>
        </div>

        {/* Metric 3: UTILIZATION */}
        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-label">STAFF UTILIZATION</span>
            <span className={`stat-badge-pill ${utilPercent > 85 ? 'warning' : 'normal'}`}>
              Counter Capacity
            </span>
          </div>
          <div className="stat-value-wrap">
            {loading ? (
              <span className="stat-loading">--</span>
            ) : (
              <div className="stat-number-row">
                <span className="stat-value font-mono">{utilPercent}</span>
                <span className="stat-unit">%</span>
              </div>
            )}
          </div>
          <div className="stat-footer-text">
            {utilPercent > 85 ? 'Counters operating near maximum load' : 'Balanced agent service capacity'}
          </div>
        </div>

        {/* Metric 4: OVERLOADED SLOTS */}
        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-label">OVERLOADED SLOTS</span>
            <span className={`stat-badge-pill ${overloadedSlots > 0 ? 'critical' : 'positive'}`}>
              {overloadedSlots > 0 ? `${overloadedSlots} Overloaded` : 'Optimal'}
            </span>
          </div>
          <div className="stat-value-wrap">
            {loading ? (
              <span className="stat-loading">--</span>
            ) : (
              <div className="stat-number-row">
                <span className={`stat-value font-mono ${overloadedSlots > 0 ? 'text-critical' : 'text-positive'}`}>
                  {overloadedSlots}
                </span>
                <span className="stat-unit">slots</span>
              </div>
            )}
          </div>
          <div className="stat-footer-text">
            {overloadedSlots > 0 ? 'Simulation flagged queue congestion' : 'Zero bottleneck intervals detected'}
          </div>
        </div>

      </div>
    </section>
  );
}
