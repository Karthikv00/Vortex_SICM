import React from 'react';
import SectionHeader from '../common/SectionHeader';
import StatusBadge from '../common/StatusBadge';

export default function AllocationPanel({
  queues = [],
  baselineAllocation = {},
  baselineResult,
  optimizedAllocation = {},
  optimizedResult
}) {
  const baseStaff = baselineAllocation?.staff_by_queue || {};
  const optStaff = optimizedAllocation?.staff_by_queue || {};
  
  const basePerQueue = baselineResult?.per_queue || {};
  const optPerQueue = optimizedResult?.per_queue || {};

  const hasOptimized = Object.keys(optStaff).length > 0;

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      gap: '16px',
      marginBottom: '20px'
    }}>
      {/* SECTION 5: Baseline Allocation */}
      <div className="cmd-card">
        <SectionHeader
          title="Baseline Allocation"
          subtitle="Static Schedule (Default 4-2-2-2)"
          badge={
            <span className="status-badge" style={{ background: 'rgba(255, 255, 255, 0.05)', color: 'var(--text-secondary)' }}>
              10 STAFF
            </span>
          }
        />

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {queues.map(q => {
            const qid = q.queue_id;
            const staff = baseStaff[qid] ?? 2;
            const m = basePerQueue[qid] || {};
            const avgWait = m.avg_wait_minutes ?? 0;
            const util = Math.round((m.utilization ?? 0) * 100);
            const isOverloaded = (m.overloaded_slots || []).length > 0;

            return (
              <div
                key={qid}
                style={{
                  background: 'rgba(0, 0, 0, 0.25)',
                  border: `1px solid ${isOverloaded ? 'var(--border-critical)' : 'var(--border-subtle)'}`,
                  borderRadius: 'var(--radius-sm)',
                  padding: '10px 12px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between'
                }}
              >
                <div>
                  <div style={{ fontWeight: 700, fontSize: '13px', color: 'var(--text-primary)' }}>
                    {q.name}
                  </div>
                  <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
                    Avg Wait: <strong style={{ color: isOverloaded ? 'var(--signal-critical)' : 'var(--text-secondary)' }}>{avgWait.toFixed(1)}m</strong> // Util: {util}%
                  </div>
                </div>

                <div style={{ textAlign: 'right' }}>
                  <div className="text-mono tabular-nums" style={{ fontSize: '16px', fontWeight: 800, color: 'var(--text-primary)' }}>
                    {staff} <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>STAFF</span>
                  </div>
                  {isOverloaded ? (
                    <span style={{ fontSize: '9px', color: 'var(--signal-critical)', fontWeight: 700 }}>
                      {m.overloaded_slots.length} OVERLOAD SLOTS
                    </span>
                  ) : (
                    <span style={{ fontSize: '9px', color: 'var(--signal-success)' }}>
                      NOMINAL
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* SECTION 6: Optimized Allocation */}
      <div className={`cmd-card ${hasOptimized ? 'with-reticles' : ''}`} style={{
        borderColor: hasOptimized ? 'var(--accent-purple)' : 'var(--border-subtle)'
      }}>
        <SectionHeader
          title="Optimized Allocation"
          subtitle="Recommended Rebalance"
          badge={
            hasOptimized ? (
              <span className="status-badge purple" style={{ fontSize: '9px' }}>
                RECOMMENDED
              </span>
            ) : (
              <span className="status-badge" style={{ fontSize: '9px', opacity: 0.5 }}>
                AWAITING RUN
              </span>
            )
          }
        />

        {!hasOptimized ? (
          <div style={{
            height: '180px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            color: 'var(--text-muted)',
            fontSize: '11px',
            fontFamily: 'var(--font-mono)'
          }}>
            <span>⚡ TRIGGER OPTIMIZER TO VIEW SHIFT DELTAS</span>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {queues.map(q => {
              const qid = q.queue_id;
              const bStaff = baseStaff[qid] ?? 2;
              const oStaff = optStaff[qid] ?? bStaff;
              const delta = oStaff - bStaff;

              const m = optPerQueue[qid] || {};
              const avgWait = m.avg_wait_minutes ?? 0;
              const util = Math.round((m.utilization ?? 0) * 100);
              const isOverloaded = (m.overloaded_slots || []).length > 0;

              return (
                <div
                  key={qid}
                  style={{
                    background: delta !== 0 ? 'rgba(176, 38, 255, 0.08)' : 'rgba(0, 0, 0, 0.25)',
                    border: delta > 0 ? '1px solid rgba(0, 255, 136, 0.4)' : (delta < 0 ? '1px solid rgba(176, 38, 255, 0.4)' : '1px solid var(--border-subtle)'),
                    borderRadius: 'var(--radius-sm)',
                    padding: '10px 12px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between'
                  }}
                >
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <span style={{ fontWeight: 700, fontSize: '13px', color: 'var(--text-primary)' }}>
                        {q.name}
                      </span>
                      {delta > 0 && (
                        <span style={{
                          background: 'var(--signal-success-dim)',
                          color: 'var(--signal-success)',
                          border: '1px solid rgba(0, 255, 136, 0.4)',
                          fontSize: '9px',
                          fontWeight: 800,
                          padding: '1px 5px',
                          borderRadius: '2px',
                          fontFamily: 'var(--font-mono)'
                        }}>
                          +{delta} STAFF ADDED
                        </span>
                      )}
                      {delta < 0 && (
                        <span style={{
                          background: 'rgba(176, 38, 255, 0.15)',
                          color: '#d67eff',
                          border: '1px solid rgba(176, 38, 255, 0.4)',
                          fontSize: '9px',
                          fontWeight: 800,
                          padding: '1px 5px',
                          borderRadius: '2px',
                          fontFamily: 'var(--font-mono)'
                        }}>
                          {delta} REALLOCATED
                        </span>
                      )}
                    </div>
                    <div style={{ fontSize: '10px', color: 'var(--text-muted)', marginTop: '2px' }}>
                      Avg Wait: <strong style={{ color: 'var(--signal-success)' }}>{avgWait.toFixed(1)}m</strong> // Util: {util}%
                    </div>
                  </div>

                  <div style={{ textAlign: 'right' }}>
                    <div className="text-mono tabular-nums" style={{ fontSize: '16px', fontWeight: 800, color: delta !== 0 ? 'var(--accent-cyan)' : 'var(--text-primary)' }}>
                      {bStaff} → <span style={{ color: 'var(--signal-success)' }}>{oStaff}</span>
                    </div>
                    <span style={{ fontSize: '9px', color: 'var(--text-muted)' }}>
                      {delta === 0 ? 'NO SHIFT' : (delta > 0 ? 'INCREASED CAPACITY' : 'SURPLUS DONATED')}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
