import React from 'react';
import ForecastChart from './ForecastChart';

export default function DemandForecast({ forecast, scenarioConfig, selectedScenario, loading }) {
  const isSurge = selectedScenario === 'surge';

  return (
    <section className="vortex-section demand-forecast-section" id="demand-forecast">
      <div className="section-title-wrap">
        <span className="section-cyan-indicator" />
        <h2 className="section-heading">DEMAND FORECAST</h2>
        <span className="section-sub-tag">EXPECTED ARRIVALS BY TIME SLOT</span>
      </div>

      <div className="vortex-card forecast-card">
        {/* Top Header & Legend */}
        <div className="forecast-card-header">
          <div className="forecast-horizon-info">
            <span className="horizon-badge font-mono">
              HORIZON: {scenarioConfig ? `${scenarioConfig.horizon_start} — ${scenarioConfig.horizon_end}` : '09:00 — 17:00'} ({forecast?.slots?.length || 32} SLOTS // {scenarioConfig?.slot_minutes || 15}-MIN INTERVALS)
            </span>
            {isSurge && (
              <span className="surge-detected-tag">
                <span className="status-dot red pulsing" />
                SURGE WINDOW ACTIVE (11:00 — 13:30)
              </span>
            )}
          </div>

          {/* Exact Required Legend: EXPECTED ARRIVALS & SURGE WINDOW */}
          <div className="forecast-legend-strip font-mono">
            <div className="legend-item">
              <span className="legend-swatch cyan" />
              <span className="legend-label">EXPECTED ARRIVALS</span>
            </div>
            <div className="legend-item">
              <span className="legend-swatch purple-amber" />
              <span className="legend-label">SURGE WINDOW</span>
            </div>
          </div>
        </div>

        {/* Chart View */}
        {loading ? (
          <div className="vortex-card-loading" style={{ height: '220px' }}>
            <span className="btn-spinner" />
            <span>LOADING FORECAST...</span>
          </div>
        ) : !forecast?.slots ? (
          <div className="vortex-card-empty" style={{ height: '220px' }}>
            <span>NO FORECAST DATA</span>
          </div>
        ) : (
          <ForecastChart forecast={forecast} scenarioConfig={scenarioConfig} selectedScenario={selectedScenario} />
        )}
      </div>
    </section>
  );
}
