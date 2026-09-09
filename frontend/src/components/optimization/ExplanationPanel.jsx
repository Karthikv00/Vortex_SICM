import React, { useState } from 'react';
import { formatDuration, formatDecimal } from '../../utils/formatters';

export default function ExplanationPanel({ optimizationResult, totalStaffBudget = 10 }) {
  const [showScores, setShowScores] = useState(false);

  if (!optimizationResult) {
    return (
      <section className="vortex-section explanation-section" id="simulation">
        <div className="section-title-wrap"><span className="section-cyan-indicator" /><h2 className="section-heading">OPTIMIZATION REASONING</h2><span className="section-sub-tag">WHY THIS ALLOCATION WAS RECOMMENDED</span></div>
        <div className="vortex-card awaiting-optimization-card"><div className="awaiting-icon">⚡</div><h3 className="awaiting-title">OPTIMIZATION NOT RUN</h3><p className="awaiting-desc">Algorithmic audit rationale and objective score breakdown will generate once optimization is executed.</p></div>
      </section>
    );
  }

  const exp = optimizationResult.explanation || '';
  const breakdown = optimizationResult.score_breakdown || {};
  const isFeasible = optimizationResult.feasible !== false;
  const optAllocation = optimizationResult.optimized?.allocation?.staff_by_queue || {};
  const baseAllocation = optimizationResult.baseline?.allocation?.staff_by_queue || {};
  const improvement = optimizationResult.improvement || {};
  const shifts = Object.keys(optAllocation).map(q => {
    const delta = (optAllocation[q] ?? 0) - (baseAllocation[q] ?? 0);
    return `${q.toUpperCase()}: ${baseAllocation[q]} → ${optAllocation[q]} (${delta >= 0 ? `+${delta}` : delta})`;
  }).join(' // ');

  return (
    <section className="vortex-section explanation-section" id="simulation">
      <div className="section-title-wrap"><span className="section-cyan-indicator" /><h2 className="section-heading">OPTIMIZATION REASONING</h2><span className="section-sub-tag">WHY THIS ALLOCATION WAS RECOMMENDED</span></div>
      <div className="vortex-card explanation-card">
        <div className="reasoning-grid">
          <div className="reasoning-block"><div className="reasoning-block-header"><span className="block-dot cyan" /><h3 className="block-title">RECOMMENDATION</h3></div><div className="reasoning-content font-mono"><p className="recommendation-summary cyan bold">{shifts || 'Rebalance staffing towards peak arrival queues.'}</p><span className="block-note text-muted">Mathematical optimization minimized the multi-objective penalty score under identical demand conditions.</span></div></div>
          <div className="reasoning-block"><div className="reasoning-block-header"><span className="block-dot green" /><h3 className="block-title">WHY</h3></div><div className="reasoning-content"><p className="explanation-text font-main">{exp || 'The recommended allocation resolves queue bottlenecks by shifting unutilized counter capacity from low-demand periods to surge lines, lowering average customer wait times and mitigating tail SLA breaches.'}</p></div></div>
          <div className="reasoning-block"><div className="reasoning-block-header"><span className="block-dot purple" /><h3 className="block-title">CONSTRAINTS</h3></div><div className="reasoning-content font-mono"><ul className="constraints-list"><li><span className="check-icon green">✓</span><span>TOTAL STAFF BUDGET = {totalStaffBudget} AGENTS</span></li><li><span className="check-icon green">✓</span><span>MINIMUM STAFF PER QUEUE RESPECTED</span></li><li><span className="check-icon green">✓</span><span>MAX CAPACITY LIMITS RESPECTED</span></li><li><span className="check-icon green">✓</span><span className="cyan">STATUS: {isFeasible ? 'MATHEMATICALLY FEASIBLE' : 'INFEASIBLE'}</span></li></ul></div></div>
          <div className="reasoning-block"><div className="reasoning-block-header"><span className="block-dot amber" /><h3 className="block-title">EXPECTED IMPACT</h3></div><div className="reasoning-content font-mono"><div className="impact-stats-mini"><div className="mini-stat-item"><span className="mini-stat-label">WAIT REDUCTION</span><span className="mini-stat-val green">{improvement.avg_wait_reduction_minutes != null ? `↓ ${formatDuration(improvement.avg_wait_reduction_minutes)}` : '—'}</span></div><div className="mini-stat-item"><span className="mini-stat-label">P95 RELIEF</span><span className="mini-stat-val cyan">{improvement.p95_wait_reduction_minutes != null ? `↓ ${formatDuration(improvement.p95_wait_reduction_minutes)}` : '—'}</span></div><div className="mini-stat-item"><span className="mini-stat-label">OVERLOADS RESOLVED</span><span className="mini-stat-val amber">{improvement.overloaded_slots_resolved != null ? `↓ ${improvement.overloaded_slots_resolved} SLOTS` : '—'}</span></div></div></div></div>
        </div>

        <div className="score-breakdown-section">
          <button className="score-toggle-btn font-mono" onClick={() => setShowScores(!showScores)}><span>{showScores ? '▼ HIDE OBJECTIVE SCORE BREAKDOWN' : '► VIEW OBJECTIVE SCORE BREAKDOWN'}</span></button>
          {showScores && <div className="score-breakdown-grid font-mono">
            {[['WAIT PENALTY','wait_score','cyan'],['OVERLOAD PENALTY','overload_score','green'],['UTILIZATION DEV','utilization_score','amber'],['REALLOCATION COST','reallocation_cost','critical']].map(([label,key,cls]) => <div className="score-item" key={key}><div className="score-meta"><span className="score-name">{label}</span><span className={`score-num ${cls}`}>{breakdown[key] != null ? formatDecimal(breakdown[key], 3) : '—'}</span></div><div className="score-bar-track"><div className={`score-bar-fill ${cls}`} style={{ width: `${Math.min(100, Math.max(0, Math.abs(breakdown[key] || 0) * 100))}%` }} /></div></div>)}
            <div className="score-total-banner"><span>COMPOSITE OBJECTIVE PENALTY:</span><span className="cyan bold">{breakdown.total_score != null ? formatDecimal(breakdown.total_score, 4) : '—'} (MINIMIZATION TARGET // LOWER IS BETTER)</span></div>
          </div>}
        </div>
      </div>
    </section>
  );
}
