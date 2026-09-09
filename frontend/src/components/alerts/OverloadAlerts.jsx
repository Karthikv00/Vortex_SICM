import React from 'react';

export default function OverloadAlerts({ simulationResult }) {
  const perQueue = simulationResult?.per_queue || {};
  
  // Extract real overload occurrences from deterministic simulation
  const alerts = [];
  Object.entries(perQueue).forEach(([qid, metrics]) => {
    const slots = metrics?.overloaded_slots || [];
    if (slots.length > 0) {
      const qTitle = qid.replace(/_/g, ' ').toUpperCase();

      slots.forEach(slotTime => {
        alerts.push({
          timeSlot: slotTime,
          queue: qTitle,
          expectedLoad: `UTIL: ${Math.round((metrics.utilization || 0) * 100)}% (AVG WAIT: ${(metrics.avg_wait_minutes || 0).toFixed(1)}M)`,
          status: 'OVERLOADED',
          severity: metrics.avg_wait_minutes > 10 ? 'CRITICAL' : 'WARNING'
        });
      });
    }
  });

  return (
    <section className="vortex-section overload-alerts-section" id="overload-alerts">
      <div className="section-title-wrap">
        <span className="section-cyan-indicator" />
        <h2 className="section-heading">OVERLOAD ALERTS</h2>
        <span className="section-sub-tag">CONGESTION BOTTLENECKS</span>
      </div>

      {alerts.length === 0 ? (
        <div className="alerts-empty-state healthy">
          <span className="status-dot green" />
          <div className="alerts-empty-content">
            <h4 className="empty-title">NO ACTIVE OVERLOADS</h4>
            <p className="empty-desc">All service lines operating within nominal queue SLA parameters.</p>
          </div>
        </div>
      ) : (
        <div className="alerts-card-list">
          {/* Summary Banner */}
          <div className="alerts-summary-banner">
            <span className="status-dot red pulsing" />
            <span className="banner-text font-mono">
              FLAGGED CONGESTION INTERVALS ({alerts.length} INSTANCES) — RESOURCE REBALANCING REQUIRED
            </span>
          </div>

          {/* Alert Items Grid */}
          <div className="alerts-table-container">
            <table className="alerts-table">
              <thead>
                <tr>
                  <th scope="col">TIME SLOT</th>
                  <th scope="col">QUEUE</th>
                  <th scope="col">EXPECTED LOAD</th>
                  <th scope="col">STATUS</th>
                </tr>
              </thead>
              <tbody>
                {alerts.map((alert, idx) => (
                  <tr key={`${alert.queue}-${alert.timeSlot}-${idx}`} className="alert-row">
                    <td className="alert-slot font-mono">{alert.timeSlot}</td>
                    <td className="alert-queue font-mono">{alert.queue}</td>
                    <td className="alert-load font-mono">{alert.expectedLoad}</td>
                    <td className="alert-status">
                      <span className={`status-pill ${alert.severity === 'CRITICAL' ? 'critical' : 'warning'}`}>
                        <span className={`status-dot ${alert.severity === 'CRITICAL' ? 'red' : 'amber'}`} />
                        {alert.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </section>
  );
}
