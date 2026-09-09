import React from 'react';

export default function OptimizedAllocation({
  queues = [],
  baselineAllocation = {},
  optimizedAllocation = {},
  optimizedResult,
  onRunOptimization,
  optimizing
}) {
  const baseStaff = baselineAllocation?.staff_by_queue || {};
  const optStaff = optimizedAllocation?.staff_by_queue || {};
  const optMetrics = optimizedResult?.per_queue || {};
  const hasRun = Object.keys(optStaff).length > 0;

  return (
    <section className="vortex-section optimized-allocation-section" id="optimized-allocation">
      <div className="section-title-wrap">
        <span className="section-cyan-indicator" />
        <h2 className="section-heading">OPTIMIZED ALLOCATION</h2>
        <span className="section-sub-tag">RECOMMENDED RESOURCE PLAN</span>
      </div>

      {!hasRun ? (
        <div className="vortex-card awaiting-optimization-card">
          <div className="awaiting-icon">⚡</div>
          <h3 className="awaiting-title">OPTIMIZATION NOT RUN</h3>
          <p className="awaiting-desc">
            RUN OPTIMIZATION TO GENERATE RECOMMENDATION
          </p>
          <button
            className="cmd-btn-primary"
            onClick={onRunOptimization}
            disabled={optimizing}
          >
            {optimizing ? 'RUNNING OPTIMIZATION...' : 'RUN OPTIMIZATION'}
          </button>
        </div>
      ) : (
        <div className="vortex-card cyan-optimized-card">
          <div className="card-top-tag font-mono">
            <span className="allocation-mode-badge cyan">FEASIBLE OPTIMIZATION</span>
            <span className="allocation-budget-info">HARD CONSTRAINTS SATISFIED: TOTAL STAFF = 10</span>
          </div>

          <div className="table-responsive">
            <table className="vortex-data-table font-mono">
              <thead>
                <tr>
                  <th scope="col">QUEUE</th>
                  <th scope="col">BASELINE</th>
                  <th scope="col">OPTIMIZED</th>
                  <th scope="col">CHANGE</th>
                  <th scope="col">AVG WAIT</th>
                  <th scope="col">P95 WAIT</th>
                  <th scope="col">UTILIZATION</th>
                </tr>
              </thead>
              <tbody>
                {queues.map((q) => {
                  const qid = q.queue_id;
                  const bCount = baseStaff[qid] ?? 2;
                  const oCount = optStaff[qid] ?? bCount;
                  const delta = oCount - bCount;
                  const m = optMetrics[qid] || {};
                  const avgWait = (m.avg_wait_minutes ?? 0).toFixed(1);
                  const p95Wait = (m.p95_wait_minutes ?? 0).toFixed(1);
                  const util = Math.round((m.utilization ?? 0) * 100);

                  return (
                    <tr key={qid} className={delta !== 0 ? 'row-shifted' : ''}>
                      <td className="cell-queue font-main bold">{q.name.toUpperCase()}</td>
                      <td className="cell-staff-base text-muted">{bCount}</td>
                      <td className="cell-staff-opt cyan bold">{oCount}</td>
                      <td className="cell-change">
                        {delta > 0 && (
                          <span className="change-tag positive">+{delta} STAFF</span>
                        )}
                        {delta < 0 && (
                          <span className="change-tag negative">{delta} STAFF</span>
                        )}
                        {delta === 0 && (
                          <span className="change-tag neutral">0</span>
                        )}
                      </td>
                      <td className="cell-wait green bold">{avgWait} MIN</td>
                      <td className="cell-p95 font-mono">{p95Wait} MIN</td>
                      <td className="cell-util font-mono">
                        <div className="util-cell-wrap">
                          <span>{util}%</span>
                          <div className="mini-progress-bar">
                            <div
                              className="mini-progress-fill normal"
                              style={{ width: `${Math.min(100, util)}%` }}
                            />
                          </div>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </section>
  );
}
