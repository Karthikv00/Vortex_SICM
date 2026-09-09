import React from 'react';

export default function BaselineAllocation({ queues = [], baselineAllocation = {}, baselineResult, totalStaffBudget = 0 }) {
  const staffByQueue = baselineAllocation?.staff_by_queue || {};
  const perQueue = baselineResult?.per_queue || {};
  const assignedTotal = Object.values(staffByQueue).reduce((a, b) => a + (Number(b) || 0), 0);

  return (
    <section className="vortex-section baseline-allocation-section" id="baseline-allocation">
      <div className="section-title-wrap"><span className="section-cyan-indicator dim" /><h2 className="section-heading">BASELINE ALLOCATION</h2><span className="section-sub-tag">CURRENT / BASIC RESOURCE PLAN</span></div>
      <div className="vortex-card neutral-dim">
        <div className="card-top-tag font-mono"><span className="allocation-mode-badge neutral">BASELINE</span><span className="allocation-budget-info">TOTAL STAFF: {assignedTotal} / {totalStaffBudget} AGENTS</span></div>
        <div className="table-responsive"><table className="vortex-data-table font-mono"><thead><tr><th scope="col">QUEUE</th><th scope="col">STAFF</th><th scope="col">AVG WAIT</th><th scope="col">P95 WAIT</th><th scope="col">UTILIZATION</th></tr></thead><tbody>
          {queues.map(q => {
            const qid = q.queue_id;
            const staff = staffByQueue[qid];
            const m = perQueue[qid] || {};
            const avgWait = m.avg_wait_minutes;
            const p95Wait = m.p95_wait_minutes;
            const util = m.utilization == null ? null : Math.round(m.utilization * 100);
            const isOverloaded = (m.overloaded_slots || []).length > 0;
            return <tr key={qid} className={isOverloaded ? 'row-overloaded' : ''}>
              <td className="cell-queue font-main bold">{q.name.toUpperCase()}</td>
              <td className="cell-staff font-mono">{staff ?? '—'}</td>
              <td className={`cell-wait font-mono ${isOverloaded ? 'critical' : ''}`}>{avgWait == null ? '—' : `${avgWait.toFixed(1)} MIN`}</td>
              <td className="cell-p95 font-mono">{p95Wait == null ? '—' : `${p95Wait.toFixed(1)} MIN`}</td>
              <td className="cell-util font-mono"><div className="util-cell-wrap"><span>{util == null ? '—' : `${util}%`}</span><div className="mini-progress-bar"><div className={`mini-progress-fill ${util > 85 ? 'critical' : util > 70 ? 'warning' : 'normal'}`} style={{ width: `${Math.min(100, util ?? 0)}%` }} /></div></div></td>
            </tr>;
          })}
        </tbody></table></div>
      </div>
    </section>
  );
}
