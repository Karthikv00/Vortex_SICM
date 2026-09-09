import React from 'react';

function formatNumber(value) {
  return new Intl.NumberFormat('en-IN', { maximumFractionDigits: 0 }).format(value || 0);
}

export default function InputDataSummary({ scenarioConfig, forecast, selectedScenario }) {
  const queues = scenarioConfig?.queues || [];
  const arrivals = forecast?.expected_arrivals || {};
  const totalCustomers = queues.reduce(
    (total, q) => total + (arrivals[q.queue_id] || []).reduce((sum, value) => sum + Number(value || 0), 0),
    0
  );
  const slotCount = forecast?.slots?.length || scenarioConfig?.slot_count || 0;
  const slotMinutes = scenarioConfig?.slot_minutes || 15;
  const totalTasks = queues.length;
  const totalStaff = scenarioConfig?.total_staff_available || 0;

  return (
    <section className="vortex-section input-data-section" id="input-data">
      <div className="section-title-wrap">
        <span className="section-cyan-indicator" />
        <h2 className="section-heading">INPUT DATA & CONSTRAINTS</h2>
        <span className="section-sub-tag">SYNTHETIC SCENARIO DEFINITION</span>
      </div>

      <div className="input-data-card vortex-card">
        <div className="input-data-intro">
          <div>
            <h3 className="input-data-title">What the model is actually consuming</h3>
            <p className="input-data-description">
              The dashboard uses deterministic synthetic branch data. Customer arrivals are generated from queue-specific base rates,
              time-of-day demand patterns, a scenario multiplier, and seeded random variation. The same scenario and seed reproduce
              the same inputs; this establishes reproducibility, not real-world predictive accuracy.
            </p>
          </div>
          <span className="input-validity-badge">VALIDATED INPUT STRUCTURE</span>
        </div>

        <div className="input-metrics-grid">
          <div className="input-metric">
            <span className="input-metric-label">CUSTOMERS / HORIZON</span>
            <strong>{formatNumber(totalCustomers)}</strong>
            <span>Expected arrivals across all queues</span>
          </div>
          <div className="input-metric">
            <span className="input-metric-label">SERVICE TASK TYPES</span>
            <strong>{totalTasks}</strong>
            <span>{queues.map(q => q.name).join(' · ') || 'No queues configured'}</span>
          </div>
          <div className="input-metric">
            <span className="input-metric-label">TIME SLOTS</span>
            <strong>{slotCount}</strong>
            <span>{slotMinutes}-minute simulation interval</span>
          </div>
          <div className="input-metric">
            <span className="input-metric-label">STAFF CONSTRAINT</span>
            <strong>{totalStaff}</strong>
            <span>Total staff budget across queues</span>
          </div>
        </div>

        <div className="input-definition-grid">
          <div className="input-definition-block">
            <h4>INPUT SYNTHESIS</h4>
            <ul>
              <li>Base arrival rates are defined per queue and per simulation slot.</li>
              <li>{selectedScenario?.toUpperCase() || 'SCENARIO'} applies its configured demand multiplier.</li>
              <li>Time-of-day demand shapes the expected inflow across the operating horizon.</li>
              <li>Seed <code>{scenarioConfig?.seed ?? 42}</code> makes the generated data reproducible.</li>
            </ul>
          </div>
          <div className="input-definition-block">
            <h4>MODEL CONSTRAINTS</h4>
            <ul>
              <li>Staff allocation must remain within each queue's minimum and maximum bounds.</li>
              <li>Total allocated staff must equal the branch staff budget.</li>
              <li>Simulation uses the configured {slotMinutes}-minute time step.</li>
              <li>Optimization compares only feasible allocations under identical demand.</li>
            </ul>
          </div>
          <div className="input-definition-block input-accuracy-block">
            <h4>HOW INPUT ACCURACY IS JUDGED</h4>
            <ul>
              <li><strong>Validity:</strong> schema, ranges, queue uniqueness, and staffing constraints are checked.</li>
              <li><strong>Reproducibility:</strong> identical scenario + seed produces identical synthetic inputs.</li>
              <li><strong>Accuracy:</strong> cannot be claimed against real bank traffic because this MVP uses synthetic data.</li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}
