import React from 'react';

export default function ErrorState({ error, onRetry }) {
  const errCode = error?.error || 'OPERATION_FAILED';
  const errMsg = error?.message || (typeof error === 'string' ? error : 'Unable to complete simulation routine.');

  return (
    <div style={{
      background: 'rgba(255, 51, 85, 0.08)',
      border: '1px solid var(--border-critical)',
      borderRadius: 'var(--radius-sm)',
      padding: '14px 18px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      gap: '14px',
      margin: '8px 0'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <span style={{ color: 'var(--signal-critical)', fontSize: '18px' }}>⚠️</span>
        <div>
          <div className="text-micro" style={{ color: 'var(--signal-critical)' }}>
            SYSTEM FAULT // {errCode}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-primary)', marginTop: '2px' }}>
            {errMsg}
          </div>
        </div>
      </div>

      {onRetry && (
        <button
          className="cmd-btn"
          onClick={onRetry}
          style={{
            background: 'var(--signal-critical-dim)',
            borderColor: 'var(--signal-critical)',
            color: 'var(--signal-critical)',
            padding: '5px 12px',
            fontSize: '10px'
          }}
        >
          RETRY
        </button>
      )}
    </div>
  );
}
