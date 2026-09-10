import React, { useState, useEffect } from 'react';
import { fetchScenarioHistory } from '../../services/api';

export default function ScenarioHistory({
  branchId = 'branch-main',
  onInspectScenario,
  refreshTrigger = 0
}) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filterType, setFilterType] = useState('all');

  const loadHistory = async () => {
    setLoading(true);
    try {
      const data = await fetchScenarioHistory(
        branchId,
        filterType === 'all' ? null : filterType
      );
      setHistory(Array.isArray(data) ? data : []);
    } catch (_) {
      setHistory([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, [branchId, filterType, refreshTrigger]);

  return (
    <section className="vortex-section scenario-history-section" id="scenario-history">
      <div className="section-title-wrap">
        <span className="section-cyan-indicator" />
        <h2 className="section-heading">SCENARIO RUN HISTORY</h2>
        <span className="section-sub-tag">SUPABASE PERSISTENCE STORE</span>
      </div>

      <div className="vortex-card scenario-history-card">
        <div className="history-header">
          <div className="history-info">
            <h3 className="history-title">Persistent Scenario Archive</h3>
            <p className="history-subtitle font-mono">
              AUDIT TRAIL OF STRESS TESTS, WHAT-IF SIMULATIONS, AND FEASIBLE ALLOCATIONS
            </p>
          </div>

          <div className="history-actions">
            <select
              className="vortex-select history-filter font-mono"
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
            >
              <option value="all">All Scenarios</option>
              <option value="stress_test">Stress Tests</option>
              <option value="what_if">What-If Runs</option>
              <option value="recovery_plan">Recovery Plans</option>
            </select>

            <button
              className="vortex-btn secondary-btn refresh-btn font-mono"
              onClick={loadHistory}
              disabled={loading}
            >
              {loading ? 'SYNCING...' : 'REFRESH ARCHIVE'}
            </button>
          </div>
        </div>

        {loading && history.length === 0 ? (
          <div className="history-empty font-mono">
            Loading historical scenario runs from database...
          </div>
        ) : history.length === 0 ? (
          <div className="history-empty font-mono">
            No saved scenarios found in persistence layer. Run a Branch Stress Test and click "Save to Scenario History".
          </div>
        ) : (
          <div className="history-grid">
            {history.map((item) => {
              const res = item.result_snapshot || {};
              const bp = res.breakpoint?.label || (res.breakpoint?.multiplier ? `~${res.breakpoint.multiplier}×` : '—');
              const bottleneck = res.bottleneck?.queue_name || res.bottleneck?.queue || '—';
              const score = res.resilienceScore ?? '—';
              const createdDate = item.created_at
                ? new Date(item.created_at).toLocaleDateString(undefined, {
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })
                : 'Just now';

              return (
                <div key={item.id} className="history-item-card">
                  <div className="history-item-top">
                    <span className="scenario-type-badge font-mono">
                      {item.scenario_type.replace('_', ' ').toUpperCase()}
                    </span>
                    <span className="scenario-date font-mono text-muted">{createdDate}</span>
                  </div>

                  <h4 className="scenario-name-text">{item.scenario_name}</h4>

                  <div className="scenario-metrics-row font-mono">
                    <div className="metric-pill">
                      <span className="lbl">RESILIENCE:</span>
                      <strong className="val cyan">{score}</strong>
                    </div>
                    <div className="metric-pill">
                      <span className="lbl">BREAKPOINT:</span>
                      <strong className="val amber">{bp}</strong>
                    </div>
                    <div className="metric-pill">
                      <span className="lbl">BOTTLENECK:</span>
                      <strong className="val text-magenta">{bottleneck}</strong>
                    </div>
                  </div>

                  <div className="history-item-actions">
                    <button
                      className="vortex-btn secondary-btn inspect-btn font-mono"
                      onClick={() => {
                        if (onInspectScenario) onInspectScenario(item);
                        const el = document.getElementById('stress-test');
                        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
                      }}
                    >
                      INSPECT SCENARIO RUN →
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </section>
  );
}
