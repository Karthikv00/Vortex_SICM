import React from 'react';

export default function EmptyState({ message = 'NO SCENARIO TELEMETRY LOADED', actionText, onAction, height = '120px' }) {
  return (
    <div style={{
      height,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '10px',
      background: 'rgba(0, 0, 0, 0.15)',
      borderRadius: 'var(--radius-sm)',
      border: '1px dashed var(--border-subtle)',
      padding: '16px',
      textAlign: 'center'
    }}>
      <div style={{ fontSize: '18px', opacity: 0.4 }}>⚡</div>
      <span className="text-micro" style={{ color: 'var(--text-muted)' }}>
        {message}
      </span>
      {actionText && onAction && (
        <button className="cmd-btn secondary" onClick={onAction} style={{ padding: '4px 12px', fontSize: '10px' }}>
          {actionText}
        </button>
      )}
    </div>
  );
}
