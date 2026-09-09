import React from 'react';
import QueueCard from './QueueCard';

export default function QueueGrid({
  queues = [],
  simulationResult,
  staffAllocation = {},
  loading
}) {
  const perQueueMetrics = simulationResult?.per_queue || {};

  return (
    <section className="vortex-section current-queues-section" id="queues">
      <div className="section-title-wrap">
        <span className="section-cyan-indicator" />
        <h2 className="section-heading">CURRENT QUEUES</h2>
        <span className="section-sub-tag">LIVE QUEUE LOAD</span>
      </div>

      {loading ? (
        <div className="vortex-card-loading">
          <span className="btn-spinner" />
          <span>CALCULATING QUEUE LOAD...</span>
        </div>
      ) : queues.length === 0 ? (
        <div className="vortex-card-empty">
          <span>NO ACTIVE QUEUE DATA</span>
        </div>
      ) : (
        <div className="queues-card-grid">
          {queues.map((q) => (
            <QueueCard
              key={q.queue_id}
              queueConfig={q}
              queueMetrics={perQueueMetrics[q.queue_id]}
              staffAssigned={staffAllocation[q.queue_id]}
            />
          ))}
        </div>
      )}
    </section>
  );
}
