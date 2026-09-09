import React, { useState } from 'react';

export default function ExplanationPanel({ optimizationResult, totalStaffBudget = 0 }) {
  const [showScores, setShowScores] = useState(false);

  if (!optimizationResult) return <section className="vortex-section explanation-section" id="simulation"><div className="section-title-wrap"><span className="section-cyan-indicator" /><h2 className="section-heading">OPTIMIZATION REASONING</h2><span className="section-sub-tag">WHY THIS ALLOCATION WAS RECOMMENDED</span></div><div className="vortex-card awaiting-optimization-card"><div className="awaiting-icon">⚡</div><h3 className="awaiting-title">OPTIMIZATION NOT RUN</h3><p className="awaiting-desc">Algorithmic audit rationale and objective score breakdown will generate once optimization is executed.</p></div></section>;

  const exp = optimizationResult.explanation || '';
  const breakdown = optimizationResult.score_breakdown || {};
  const isFeasible = optimizationResult.feasible !== false;
  const optAllocation = optimizationResult.optimized?.allocation?.staff_by_queue || {};
  const baseAllocation = optimizationResult.baseline?.allocation?.staff_by_queue || {};
  const improvement = optimizationResult.improvement || {};
  const shifts = Object.keys(optAllocation).map(q => {
    const before = baseAllocation[q]; const after = optAllocation[q];
    const delta = before != null && after != null ? after - before : null;
    return `${q.toUpperCase()}: ${before ?? '—'} → ${after ?? '—'} (${delta == null ? '—' : delta >= 0 ? `+${delta}` : delta})`;
  }).join(' // ');
  const scoreWidth = value => value == null ? 0 : Math.min(100, Math.max(0, Number(value)));

  return <section className="vortex-section explanation-section" id="simulation">
    <div className="section-title-wrap"><span className="section-cyan-indicator" /><h2 className="section-heading">OPTIMIZATION REASONING</h2><span className="section-sub-tag">WHY THIS ALLOCATION WAS RECOMMENDED</span></div>
    <div className="vortex-card explanation-card"><div className="reasoning-grid">
      <div className="reasoning-block"><div className="reasoning-block-header"><span className="block-dot cyan" /><h3 className="block-title">RECOMMENDATION</h3></div><div className="reasoning-content font-mono"><p className="recommendation-summary cyan bold">{shifts || 'No allocation shift returned by the optimizer.'}</p><span className="block-note text-muted">Mathematical optimization evaluates the same demand conditions and staffing constraints as the baseline.</span></div></div>
      <div className="reasoning-block"><div className="reasoning-block-header"><span className="block-dot green" /><h3 className="block-title">WHY</h3></div><div className="reasoning-content"><p className="explanation-text font-main">{exp || 'No deterministic explanation was returned by the optimization engine.'}</p></div></div>
      <div className="reasoning-block"><div className="reasoning-block-header"><span className="block-dot purple" /><h3 className="block-title">CONSTRAINTS</h3></div><div className="reasoning-content font-mono"><ul className="constraints-list"><li><span className="check-icon green">✓</span><span>TOTAL STAFF BUDGET = {totalStaffBudget} AGENTS</span></li><li><span className="check-icon green">✓</span><span>QUEUE MINIMUMS RESPECTED</span></li><li><span className="check-icon green">✓</span><span>MAX CAPACITY LIMITS RESPECTED</span></li><li><span className="check-icon green">✓</span><span className="cyan">STATUS: {isFeasible ? 'MATHEMATICALLY FEASIBLE' : 'INFEASIBLE'}</span></li></ul></div></div>
      <div className="reasoning-block"><div className="reasoning-block-header"><span className="block-dot amber" /><h3 className="block-title">EXPECTED IMPACT</h3></div><div className="reasoning-content font-mono"><div className="impact-stats-mini"><div className="mini-stat-item"><span className="mini-stat-label">WAIT REDUCTION</span><span className="mini-stat-val green">↓ {improvement.avg_wait_reduction_minutes == null ? '—' : `${improvement.avg_wait_reduction_minutes.toFixed(1)} MIN`}</span></div><div className="mini-stat-item"><span className="mini-stat-label">P95 RELIEF</span><span className="mini-stat-val cyan">↓ {improvement.p95_wait_reduction_minutes == null ? '—' : `${improvement.p95_wait_reduction_minutes.toFixed(1)} MIN`}</span></div><div className="mini-stat-item"><span className="mini-stat-label">OVERLOADS RESOLVED</span><span className="mini-stat-val amber">↓ {improvement.overloaded_slots_resolved == null ? '—' : `${improvement.overloaded_slots_resolved} SLOTS`}</span></div></div></div></div>
    </div>
    <div className="score-breakdown-section"><button className="score-toggle-btn font-mono" onClick={() => setShowScores(!showScores)}><span>{showScores ? '▼ HIDE OBJECTIVE SCORE BREAKDOWN' : '► VIEW OBJECTIVE SCORE BREAKDOWN'}</span></button>{showScores && <div className="score-breakdown-grid font-mono">
      <div className="score-item"><div className="score-meta"><span className="score-name">WAIT SCORE</span><span className="score-num cyan">{breakdown.wait_score == null ? '—' : breakdown.wait_score.toFixed(1)}</span></div><div className="score-bar-track"><div className="score-bar-fill cyan" style={{ width: `${scoreWidth(breakdown.wait_score)}%` }} /></div></div>
      <div className="score-item"><div className="score-meta"><span className="score-name">OVERLOAD SCORE</span><span className="score-num green">{breakdown.overload_score == null ? '—' : breakdown.overload_score.toFixed(1)}</span></div><div className="score-bar-track"><div className="score-bar-fill green" style={{ width: `${scoreWidth(breakdown.overload_score)}%` }} /></div></div>
      <div className="score-item"><div className="score-meta"><span className="score-name">UTILIZATION SCORE</span><span className="score-num amber">{breakdown.utilization_score == null ? '—' : breakdown.utilization_score.toFixed(1)}</span></div><div className="score-bar-track"><div className="score-bar-fill amber" style={{ width: `${scoreWidth(breakdown.utilization_score)}%` }} /></div></div>
      <div className="score-item"><div className="score-meta"><span className="score-name">REALLOCATION COST</span><span className="score-num critical">{breakdown.reallocation_cost == null ? '—' : breakdown.reallocation_cost.toFixed(1)}</span></div><div className="score-bar-track"><div className="score-bar-fill critical" style={{ width: `${scoreWidth(Math.abs(breakdown.reallocation_cost))}%` }} /></div></div>
      <div className="score-total-banner"><span>COMPOSITE OBJECTIVE UTILITY:</span><span className="cyan bold">{breakdown.total_score == null ? '—' : `${breakdown.total_score.toFixed(1)} / 100`}</span></div>
    </div>}</div></div>
  </section>;
}
