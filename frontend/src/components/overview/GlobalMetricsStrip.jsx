import React from 'react';
import { formatDuration } from '../../utils/formatters';

export default function GlobalMetricsStrip({ simulationResult, loading }) {
  const branchMetrics = simulationResult?.branch_wide;
  const avgWait = branchMetrics?.avg_wait_minutes ?? 0;
  const p95Wait = branchMetrics?.p95_wait_minutes ?? 0;
  const queueList = Object.values(simulationResult?.per_queue || {});
  const avgUtil = queueList.length > 0 ? queueList.reduce((sum, q) => sum + (q.utilization ?? 0), 0) / queueList.length : 0;
  const utilPercent = Math.round(avgUtil * 100);
  const overloadedSlots = branchMetrics?.overloaded_slot_count ?? 0;

  return (
    <section className="vortex-section global-metrics-section" id="global-metrics">
      <div className="metrics-cards-grid">
        <div className="stat-card hero-dark-card"><div className="stat-card-header"><span className="stat-label">AVG WAIT TIME</span><span className="stat-badge-trend positive">{avgWait <= 8 ? 'Nominal SLA' : 'Exceeding SLA'}</span></div><div className="stat-value-wrap">{loading ? <span className="stat-loading">--</span> : <div className="stat-number-row"><span className="stat-value font-mono stat-duration">{formatDuration(avgWait)}</span></div>}</div><div className="stat-footer-text">{avgWait > 8 ? 'High branch congestion detected' : 'Within target operations tolerance'}</div></div>
        <div className="stat-card"><div className="stat-card-header"><span className="stat-label">P95 WAIT TIME</span><span className={`stat-badge-pill ${p95Wait > 15 ? 'critical' : 'normal'}`}>Tail Latency</span></div><div className="stat-value-wrap">{loading ? <span className="stat-loading">--</span> : <div className="stat-number-row"><span className={`stat-value font-mono stat-duration ${p95Wait > 15 ? 'text-critical' : ''}`}>{formatDuration(p95Wait)}</span></div>}</div><div className="stat-footer-text">95% of branch visitors served within this window</div></div>
        <div className="stat-card"><div className="stat-card-header"><span className="stat-label">STAFF UTILIZATION</span><span className={`stat-badge-pill ${utilPercent > 85 ? 'warning' : 'normal'}`}>Counter Capacity</span></div><div className="stat-value-wrap">{loading ? <span className="stat-loading">--</span> : <div className="stat-number-row"><span className="stat-value font-mono">{utilPercent}</span><span className="stat-unit">%</span></div>}</div><div className="stat-footer-text">{utilPercent > 85 ? 'Counters operating near maximum load' : 'Balanced agent service capacity'}</div></div>
        <div className="stat-card"><div className="stat-card-header"><span className="stat-label">OVERLOADED SLOTS</span><span className={`stat-badge-pill ${overloadedSlots > 0 ? 'critical' : 'positive'}`}>{overloadedSlots > 0 ? `${overloadedSlots} Overloaded` : 'Optimal'}</span></div><div className="stat-value-wrap">{loading ? <span className="stat-loading">--</span> : <div className="stat-number-row"><span className={`stat-value font-mono ${overloadedSlots > 0 ? 'text-critical' : 'text-positive'}`}>{overloadedSlots}</span><span className="stat-unit">slots</span></div>}</div><div className="stat-footer-text">{overloadedSlots > 0 ? 'Simulation flagged queue congestion' : 'Zero bottleneck intervals detected'}</div></div>
      </div>
    </section>
  );
}
