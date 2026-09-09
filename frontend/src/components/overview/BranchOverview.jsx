import React from 'react';

export default function BranchOverview({
  scenarioConfig,
  selectedScenario
}) {
  const branchName = scenarioConfig?.branch_name || 'Central Bank Branch';
  const hours = `${scenarioConfig?.horizon_start || '09:00'} — ${scenarioConfig?.horizon_end || '17:00'}`;
  const totalStaff = scenarioConfig?.total_staff_available ?? 10;
  const scenarioLabel = (selectedScenario || 'normal').toUpperCase();

  return (
    <section className="vortex-section branch-overview-section" id="branch-overview">
      <div className="section-title-wrap">
        <span className="section-cyan-indicator" />
        <h2 className="section-heading">BRANCH OVERVIEW</h2>
        <span className="section-sub-tag">FACILITY TELEMETRY</span>
      </div>

      <div className="branch-overview-card">
        <div className="branch-item">
          <span className="branch-item-label">BRANCH</span>
          <span className="branch-item-val highlight">{branchName}</span>
        </div>

        <div className="branch-divider-v" />

        <div className="branch-item">
          <span className="branch-item-label">OPERATING HOURS</span>
          <span className="branch-item-val font-mono">{hours}</span>
        </div>

        <div className="branch-divider-v" />

        <div className="branch-item">
          <span className="branch-item-label">TOTAL STAFF</span>
          <span className="branch-item-val font-mono staff-count">
            {totalStaff} <span className="branch-unit">ACTIVE AGENTS</span>
          </span>
        </div>

        <div className="branch-divider-v" />

        <div className="branch-item">
          <span className="branch-item-label">SCENARIO</span>
          <div className="scenario-badge-wrap">
            <span className={`scenario-status-pill ${selectedScenario}`}>
              <span className={`status-dot ${selectedScenario === 'surge' ? 'red pulsing' : (selectedScenario === 'peak' ? 'amber' : 'green')}`} />
              {scenarioLabel}
            </span>
          </div>
        </div>
      </div>
    </section>
  );
}
