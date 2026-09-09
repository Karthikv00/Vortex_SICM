import React from 'react';

export default function QueueCard({
  queueConfig,
  queueMetrics,
  staffAssigned
}) {
  const qName = queueConfig?.name || 'Service Queue';
  const avgWait = queueMetrics?.avg_wait_minutes ?? 0;
  const utilization = queueMetrics?.utilization ?? 0;
  const utilPercent = Math.round(utilization * 100);
  const overloadedSlots = queueMetrics?.overloaded_slots || [];
  const isOverloaded = overloadedSlots.length > 0;
  const isWatch = !isOverloaded && (avgWait > 6.0 || utilPercent >= 75);

  let statusLabel = 'NORMAL';
  let statusClass = 'normal';
  if (isOverloaded) {
    statusLabel = 'OVERLOADED';
    statusClass = 'critical';
  } else if (isWatch) {
    statusLabel = 'WATCH';
    statusClass = 'warning';
  }

  return (
    <div className={`queue-card ${statusClass}`}>
      {/* Top Header: Queue Name & Status */}
      <div className="queue-card-top">
        <div className="queue-name-wrap">
          <span className="queue-tag-code">{queueConfig?.queue_id?.toUpperCase()}</span>
          <h3 className="queue-name">{qName}</h3>
        </div>
        <div className={`queue-status-badge ${statusClass}`}>
          <span className={`status-dot ${statusClass === 'critical' ? 'red pulsing' : (statusClass === 'warning' ? 'amber' : 'green')}`} />
          <span>{statusLabel}</span>
        </div>
      </div>

      {/* Grid of Key Queue Metrics */}
      <div className="queue-metrics-grid">
        
        {/* CURRENT STAFF */}
        <div className="queue-metric-item">
          <span className="queue-metric-label">CURRENT STAFF</span>
          <div className="queue-metric-value-row">
            <span className="queue-metric-num font-mono cyan">
              {staffAssigned !== undefined && staffAssigned !== null ? staffAssigned : '—'}
            </span>
            <span className="queue-metric-sub font-mono">AGENTS</span>
          </div>
          <span className="queue-metric-limit">LIMIT: {queueConfig?.min_staff} — {queueConfig?.max_staff}</span>
        </div>

        {/* AVG WAIT */}
        <div className="queue-metric-item">
          <span className="queue-metric-label">AVG WAIT</span>
          <div className="queue-metric-value-row">
            <span className={`queue-metric-num font-mono ${statusClass === 'critical' ? 'critical' : (statusClass === 'warning' ? 'warning' : 'normal')}`}>
              {queueMetrics ? avgWait.toFixed(1) : '—'}
            </span>
            <span className="queue-metric-sub font-mono">MIN</span>
          </div>
          <span className="queue-metric-limit">P95: {queueMetrics?.p95_wait_minutes != null ? `${queueMetrics.p95_wait_minutes.toFixed(1)}m` : '—'}</span>
        </div>

        {/* UTILIZATION */}
        <div className="queue-metric-item">
          <span className="queue-metric-label">UTILIZATION</span>
          <div className="queue-metric-value-row">
            <span className={`queue-metric-num font-mono ${utilPercent > 85 ? 'critical' : (utilPercent > 70 ? 'warning' : 'normal')}`}>
              {queueMetrics ? utilPercent : '—'}
            </span>
            <span className="queue-metric-sub font-mono">%</span>
          </div>
          <span className="queue-metric-limit">CAPACITY RATIO</span>
        </div>

      </div>

      {/* Load Capacity Bar */}
      <div className="queue-load-bar-wrap">
        <div className="queue-load-bar-track">
          <div
            className={`queue-load-bar-fill ${statusClass}`}
            style={{ width: `${Math.min(100, utilPercent)}%` }}
          />
        </div>
      </div>

      {/* Overload Notice if applicable */}
      {isOverloaded && (
        <div className="queue-overload-notice">
          <span className="overload-icon">⚠</span>
          <span className="overload-text font-mono">
            {overloadedSlots.length} OVERLOAD SLOTS ({overloadedSlots.slice(0, 3).join(', ')}{overloadedSlots.length > 3 ? '...' : ''})
          </span>
        </div>
      )}
    </div>
  );
}
