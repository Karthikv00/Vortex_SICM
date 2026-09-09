import React from 'react';

function formatNumber(value) {
  return new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 }).format(value || 0);
}

export default function InputDataSummary({ scenarioConfig, forecast, selectedScenario }) {
  const queues = scenarioConfig?.queues || [];
  const arrivals = forecast?.expected_arrivals || {};
  const totalCustomers = queues.reduce((total, q) => total + (arrivals[q.queue_id] || []).reduce((sum, value) => sum + Number(value || 0), 0), 0);
  const slotCount = forecast?.slots?.length || 0;
  const slotMinutes = scenarioConfig?.slot_minutes || 15;
  const totalTasks = queues.length;
  const totalStaff = scenarioConfig?.total_staff_available || 0;

  return (
    <section className="vortex-section input-data-section" id="input-data">
      <div className="section-title-wrap"><span className="section-cyan-indicator" /><h2 className="section-heading">INPUT DATA & CONSTRAINTS</h2><span className="section-sub-tag">SYNTHETIC SCENARIO DEFINITION</span></div>
      <div className="input-data-card vortex-card">
        <div className="input-data-intro"><div><h3 className="input-data-title">What the model is actually consuming</h3><p className="input-data-description">The dashboard uses deterministic synthetic branch data. Customer arrivals are generated from queue-specific base rates, time-of-day demand patterns, a scenario multiplier, and seeded random variation. The same scenario and seed reproduce the same inputs; this establishes reproducibility, not real-world predictive accuracy.</p></div><span className="input-validity-badge">VALIDATED INPUT STRUCTURE</span></div>

        <div className="input-metrics-grid">
          <div className="input-metric"><span className="input-metric-label">CUSTOMERS / HORIZON</span><strong>{formatNumber(totalCustomers)}</strong><span>Expected arrivals across all queues</span></div>
          <div className="input-metric"><span className="input-metric-label">SERVICE TASK TYPES</span><strong>{totalTasks}</strong><span>{queues.map(q => q.name).join(' · ') || 'No queues configured'}</span></div>
          <div className="input-metric"><span className="input-metric-label">TIME SLOTS</span><strong>{slotCount}</strong><span>{slotMinutes}-minute simulation interval</span></div>
          <div className="input-metric"><span className="input-metric-label">STAFF CONSTRAINT</span><strong>{totalStaff}</strong><span>Total staff budget across queues</span></div>
        </div>

        <div className="input-table-wrap">
          <div className="input-table-heading">SYNTHESIZED INPUTS BY SERVICE QUEUE</div>
          <table className="input-table"><thead><tr><th>QUEUE / TASK</th><th>EXPECTED CUSTOMERS</th><th>AVG SERVICE</th><th>STAFF BOUNDS</th><th>INPUT SOURCE</th></tr></thead><tbody>
            {queues.map(q => {
              const queueCustomers = (arrivals[q.queue_id] || []).reduce((sum, value) => sum + Number(value || 0), 0);
              return <tr key={q.queue_id}><td><strong>{q.name}</strong><span>{q.queue_id.toUpperCase()}</span></td><td>{formatNumber(queueCustomers)} / horizon</td><td>{q.avg_service_time_minutes} min</td><td>{q.min_staff} — {q.max_staff} agents</td><td>Seeded synthetic</td></tr>;
            })}
          </tbody></table>
        </div>
      </div>
    </section>
  );
}
