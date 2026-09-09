import React from 'react';

export default function ComparisonMatrix({ optimizationResult, baselineResult, onOptimizeClick, optimizing }) {
  const hasRun = !!optimizationResult;
  if (!hasRun) return <section className="vortex-section optimization-impact-section" id="optimization"><div className="section-title-wrap"><span className="section-cyan-indicator" /><h2 className="section-heading">OPTIMIZATION IMPACT</h2><span className="section-sub-tag">PERFORMANCE DELTAS</span></div><div className="vortex-card awaiting-optimization-card"><div className="awaiting-icon">⚡</div><h3 className="awaiting-title">AWAITING OPTIMIZATION</h3><p className="awaiting-desc">Trigger the optimization solver to calculate comparative wait, tail latency, and congestion mitigation deltas.</p><button className="cmd-btn-primary" onClick={onOptimizeClick} disabled={optimizing}>{optimizing ? 'RUNNING OPTIMIZATION...' : 'RUN OPTIMIZATION'}</button></div></section>;

  const base = optimizationResult.baseline?.result?.branch_wide || baselineResult?.branch_wide || {};
  const opt = optimizationResult.optimized?.result?.branch_wide || {};
  const improvement = optimizationResult.improvement || {};
  const avgWaitBefore = base.avg_wait_minutes;
  const avgWaitAfter = opt.avg_wait_minutes;
  const avgWaitReduction = improvement.avg_wait_reduction_minutes;
  const p95Before = base.p95_wait_minutes;
  const p95After = opt.p95_wait_minutes;
  const p95Reduction = improvement.p95_wait_reduction_minutes;
  const overloadsBefore = base.overloaded_slot_count;
  const overloadsAfter = opt.overloaded_slot_count;
  const overloadsResolved = improvement.overloaded_slots_resolved;
  const fmt = (v, suffix = '') => v == null ? '—' : `${v.toFixed(1)}${suffix}`;
  const baseScore = optimizationResult.baseline?.score;
  const optScore = optimizationResult.optimized?.score;
  const scoreText = baseScore == null || optScore == null ? '—' : `${baseScore.toFixed(1)} → ${optScore.toFixed(1)} (+${(optScore - baseScore).toFixed(1)} PTS)`;

  return <section className="vortex-section optimization-impact-section" id="optimization">
    <div className="section-title-wrap"><span className="section-cyan-indicator" /><h2 className="section-heading">OPTIMIZATION IMPACT</h2><span className="section-sub-tag">BEFORE / AFTER COMPARISON</span></div>
    <div className="vortex-card impact-hero-card"><div className="impact-cards-grid">
      <div className="impact-metric-box"><div className="impact-label-row"><span className="impact-metric-name">AVERAGE WAIT</span><span className="impact-code font-mono">SLA CORE</span></div><div className="impact-transition-row font-mono"><span className="val-before text-muted">{fmt(avgWaitBefore, ' MIN')}</span><span className="transition-arrow">→</span><span className="val-after green bold">{fmt(avgWaitAfter, ' MIN')}</span></div><div className="impact-delta-pill positive font-mono"><span className="arrow-down">↓</span><span>{fmt(avgWaitReduction, ' MIN')}</span><span className="pct-tag">({avgWaitBefore > 0 && avgWaitReduction != null ? ((avgWaitReduction / avgWaitBefore) * 100).toFixed(0) : '—'}% RELIEF)</span></div></div>
      <div className="impact-metric-box"><div className="impact-label-row"><span className="impact-metric-name">P95 WAIT</span><span className="impact-code font-mono">TAIL RISK</span></div><div className="impact-transition-row font-mono"><span className="val-before text-muted">{fmt(p95Before, ' MIN')}</span><span className="transition-arrow">→</span><span className="val-after green bold">{fmt(p95After, ' MIN')}</span></div><div className="impact-delta-pill positive font-mono"><span className="arrow-down">↓</span><span>{fmt(p95Reduction, ' MIN')}</span><span className="pct-tag">WORST-CASE RELIEF</span></div></div>
      <div className="impact-metric-box"><div className="impact-label-row"><span className="impact-metric-name">OVERLOADED SLOTS</span><span className="impact-code font-mono">BOTTLENECKS</span></div><div className="impact-transition-row font-mono"><span className="val-before critical">{overloadsBefore == null ? '—' : `${overloadsBefore} SLOTS`}</span><span className="transition-arrow">→</span><span className={`val-after bold ${overloadsAfter === 0 ? 'green' : 'amber'}`}>{overloadsAfter == null ? '—' : `${overloadsAfter} SLOTS`}</span></div><div className="impact-delta-pill positive font-mono"><span className="arrow-down">↓</span><span>{overloadsResolved == null ? '—' : `${overloadsResolved} RESOLVED`}</span><span className="pct-tag">CONGESTION INTERVALS</span></div></div>
    </div><div className="impact-card-footer font-mono"><span className="footer-audit-note">MATHEMATICAL MODEL: M/M/C SIMULATION & KNAPSACK HEURISTIC SOLVER</span><span className="footer-score-note cyan">EVALUATION SCORE: {scoreText}</span></div></div>
  </section>;
}
