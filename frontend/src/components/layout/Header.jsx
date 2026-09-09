import React from 'react';

export default function Header({ selectedScenario = 'normal', onOptimize, optimizing, hasScenario, onMobileToggle }) {
  const dotColor = selectedScenario === 'surge' ? 'red pulsing' : (selectedScenario === 'peak' ? 'amber' : 'green');

  return (
    <header className="vortex-top-header">
      <div className="header-inner">
        <div className="header-left">
          {onMobileToggle && (
            <button className="mobile-sidebar-toggle" onClick={onMobileToggle} aria-label="Toggle sidebar navigation">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="3" y1="12" x2="21" y2="12" /><line x1="3" y1="6" x2="21" y2="6" /><line x1="3" y1="18" x2="21" y2="18" />
              </svg>
            </button>
          )}
          <div className="header-titles">
            <div className="header-primary-row">
              <span className="header-reticle-dot" />
              <h1 className="header-title">QUEUEWISE</h1>
              <span className="header-code-tag">JP-012</span>
            </div>
            <div className="header-secondary-label">BANK OPERATIONS DECISION SUPPORT</div>
          </div>
        </div>

        <div className="header-right">
          <div className="scenario-selector-group">
            <span className="scenario-group-label">OPERATING SCENARIO</span>
            <div className="scenario-pill-strip auto-classified" role="status" aria-label="Operating Scenario">
              <span className={`scenario-btn ${selectedScenario} active auto-pill font-mono`}>
                <span className={`status-dot ${dotColor}`} />
                {selectedScenario.toUpperCase()} (WORKLOAD-DRIVEN)
              </span>
            </div>
          </div>
          <button className="cmd-btn-optimize" onClick={onOptimize} disabled={!hasScenario || optimizing} title="Execute mathematical resource optimization engine">
            {optimizing ? <><span className="btn-spinner" /><span>RUNNING OPTIMIZATION...</span></> : <><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" /></svg><span>RUN OPTIMIZATION</span></>}
          </button>
        </div>
      </div>
    </header>
  );
}
